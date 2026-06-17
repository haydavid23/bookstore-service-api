"""Database/query logic for the book catalog.

Everything that touches the SQLAlchemy session or builds a query lives here so
the route handlers in book_catalog.py stay thin. Functions return raw rows or
model instances; serialization and in-Python post-processing live in utils.py.
"""

from sqlalchemy import func, literal_column
from sqlalchemy.dialects.postgresql import aggregate_order_by

from extensions import db
from models import (
    Author,
    AuthorPublisher,
    Book,
    BookAuthor,
    BookGenre,
    Genre,
    OrderedItem,
    Publisher,
    Review,
)

from blueprints.book_catalog.utils import compute_discounted_price


def top_seller_counts():
    """Return {book_id: total_sold} for every book that has been ordered.

    Empty dict when nothing has sold. The caller decides how to rank/cap.
    """
    sold_count = func.count(OrderedItem.id)
    rows = (
        db.session.query(
            OrderedItem.book_id,
            sold_count.label("total_sold"),
        )
        .group_by(OrderedItem.book_id)
        .order_by(sold_count.desc())
        .all()
    )
    return {row.book_id: int(row.total_sold) for row in rows}


def _average_rating_subquery():
    """Average review rating for one book as a correlated scalar subquery.

    Correlated so the author/genre joins below can't inflate the count.
    NULL when a book has no reviews.
    """
    return (
        db.session.query(func.avg(Review.rating))
        .filter(Review.book_id == Book.id)
        .correlate(Book)
        .scalar_subquery()
    )


def _authors_subquery():
    """One row per book_id with its authors combined alphabetically."""
    author_full_name = Author.name + " " + Author.lastname
    return (
        db.session.query(
            BookAuthor.book_id.label("book_id"),
            func.string_agg(
                author_full_name,
                aggregate_order_by(literal_column("', '"), author_full_name),
            ).label("authors"),
        )
        .join(Author, Author.id == BookAuthor.author_id)
        .group_by(BookAuthor.book_id)
        .subquery()
    )


def _genres_subquery():
    """One row per book_id with its genres combined alphabetically."""
    return (
        db.session.query(
            BookGenre.book_id.label("book_id"),
            func.string_agg(
                Genre.genre,
                aggregate_order_by(literal_column("', '"), Genre.genre),
            ).label("genres"),
        )
        .join(Genre, Genre.id == BookGenre.genre_id)
        .group_by(BookGenre.book_id)
        .subquery()
    )


def _publishers_subquery():
    """One row per book_id with its publishers (via author) combined alphabetically.

    Distinct first because several of a book's authors can share a publisher.
    """
    book_publishers = (
        db.session.query(
            BookAuthor.book_id.label("book_id"),
            Publisher.name.label("publisher_name"),
        )
        .join(AuthorPublisher, AuthorPublisher.author_id == BookAuthor.author_id)
        .join(Publisher, Publisher.id == AuthorPublisher.publisher_id)
        .distinct()
        .subquery()
    )
    return (
        db.session.query(
            book_publishers.c.book_id.label("book_id"),
            func.string_agg(
                book_publishers.c.publisher_name,
                aggregate_order_by(
                    literal_column("', '"), book_publishers.c.publisher_name
                ),
            ).label("publishers"),
        )
        .group_by(book_publishers.c.book_id)
        .subquery()
    )


def _genre_exists_filter(genre):
    """EXISTS clause matching books that have the given genre (case-insensitive).

    Used instead of re-joining the genre table so each book stays a single row.
    """
    return (
        db.session.query(BookGenre.book_id)
        .join(Genre, Genre.id == BookGenre.genre_id)
        .filter(BookGenre.book_id == Book.id)
        .filter(func.lower(Genre.genre) == genre.strip().lower())
        .exists()
    )


def _author_exists_filter(author_id):
    """EXISTS clause matching books written by the given author id.

    Like the genre filter, this keeps each book a single row instead of
    re-joining the author tables into the main query.
    """
    return (
        db.session.query(BookAuthor.book_id)
        .filter(BookAuthor.book_id == Book.id)
        .filter(BookAuthor.author_id == author_id)
        .exists()
    )


def fetch_catalog_rows(*, genre=None, author_id=None, book_ids=None):
    """Run the catalog query and return raw rows (exactly one per book).

    authors, genres, and publishers are pre-aggregated into one row per book_id
    and LEFT JOINed onto book, so books with no authors/genres/publishers are
    still returned (those fields come back NULL) and nothing is duplicated.

    genre      -> optional case-insensitive genre filter.
    author_id  -> optional author id; only books by this author are returned.
    book_ids   -> optional iterable restricting the result to these book ids.
    """
    avg_rating = _average_rating_subquery()
    authors_subq = _authors_subquery()
    genres_subq = _genres_subquery()
    publishers_subq = _publishers_subquery()

    query = (
        db.session.query(
            Book.id,
            Book.isbn,
            Book.name,
            Book.description,
            Book.price,
            Book.year_published,
            authors_subq.c.authors.label("author"),
            genres_subq.c.genres.label("genre"),
            publishers_subq.c.publishers.label("publisher"),
            avg_rating.label("average_rating"),
        )
        .outerjoin(authors_subq, authors_subq.c.book_id == Book.id)
        .outerjoin(genres_subq, genres_subq.c.book_id == Book.id)
        .outerjoin(publishers_subq, publishers_subq.c.book_id == Book.id)
    )

    if book_ids is not None:
        query = query.filter(Book.id.in_(book_ids))

    if genre:
        query = query.filter(_genre_exists_filter(genre))

    if author_id is not None:
        query = query.filter(_author_exists_filter(author_id))

    return query.all()


def find_publisher_by_name(name):
    """Look up a publisher by name (case-insensitive). None if not found."""
    return Publisher.query.filter(
        func.lower(Publisher.name) == name.strip().lower()
    ).first()


def _books_for_publisher(publisher_id):
    """Books linked to a publisher through their authors.

        book -> bookauthor -> author_publisher -> publisher

    distinct() so a book with two matching authors is only returned once.
    """
    return (
        Book.query.join(BookAuthor, Book.id == BookAuthor.book_id)
        .join(AuthorPublisher, AuthorPublisher.author_id == BookAuthor.author_id)
        .filter(AuthorPublisher.publisher_id == publisher_id)
        .distinct()
        .all()
    )


def apply_publisher_discount(publisher_id, discount_value):
    """Apply a percentage discount to every priced book from a publisher.

    Commits the change and returns the number of books matched. Raises
    SQLAlchemyError if the commit fails (the caller is responsible for rollback).
    """
    books = _books_for_publisher(publisher_id)
    for book in books:
        if book.price is not None:
            book.price = compute_discounted_price(book.price, discount_value)

    db.session.commit()
    return len(books)
