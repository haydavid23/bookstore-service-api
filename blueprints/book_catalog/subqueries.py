"""SELECT-side query building for the book catalog.

Builds the enriched per-book SELECT used by the catalog: authors, genres, and
publishers are each pre-aggregated into one row per book_id and LEFT JOINed onto
book, and the average review rating comes in as a correlated scalar subquery.
Keeping this here lets service.py stay thin orchestration.
"""

from sqlalchemy import func, literal_column
from sqlalchemy.dialects.postgresql import aggregate_order_by

from extensions import db
from models import (
    Author,
    Book,
    BookAuthor,
    BookGenre,
    Genre,
    Publisher,
    Review,
)


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
        .join(Author, Author.id == BookAuthor.author_id)
        .join(Publisher, Publisher.id == Author.publisher_id)
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


def base_catalog_query():
    """The enriched catalog SELECT with no filters applied.

    authors, genres, and publishers are pre-aggregated into one row per book_id
    and LEFT JOINed onto book, so books with no authors/genres/publishers are
    still returned (those fields come back NULL) and nothing is duplicated. The
    caller applies any WHERE clauses (see filters.py) and runs the query.
    """
    avg_rating = _average_rating_subquery()
    authors_subq = _authors_subquery()
    genres_subq = _genres_subquery()
    publishers_subq = _publishers_subquery()

    return (
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
