"""Database/query logic for the book catalog.

Everything that touches the SQLAlchemy session or builds a query lives here so
the route handlers in book_catalog.py stay thin. The enriched catalog SELECT is
built in subqueries.py and the WHERE clauses in filters.py; this module wires
them together and holds the remaining publisher/discount queries. Functions
return raw rows or model instances; serialization and in-Python post-processing
live in utils.py.
"""

from sqlalchemy import func

from extensions import db
from models import (
    Author,
    Book,
    BookAuthor,
    BookGenre,
    Genre,
    Publisher,
)

from blueprints.book_catalog.filters import catalog_filters
from blueprints.book_catalog.subqueries import base_catalog_query
from blueprints.book_catalog.utils import compute_discounted_price


def top_seller_counts():
    """Return {book_id: copies_sold} for every book, ranked by copies_sold desc.

    Sales are tracked directly on book.copies_sold, so ranking reads that column
    instead of counting ordered_items rows. Books with a NULL copies_sold are
    skipped. The caller decides how to cap the ranked list.
    """
    rows = (
        db.session.query(Book.id, Book.copies_sold)
        .filter(Book.copies_sold.isnot(None))
        .order_by(Book.copies_sold.desc())
        .all()
    )
    return {row.id: int(row.copies_sold) for row in rows}


def fetch_catalog_rows(*, genre=None, author_id=None, book_ids=None, isbn=None):
    """Run the catalog query and return raw rows (exactly one per book).

    The enriched SELECT (authors/genres/publishers/average_rating) comes from
    base_catalog_query(); the supplied criteria are turned into WHERE clauses by
    catalog_filters() and applied here.

    genre      -> optional case-insensitive genre filter.
    author_id  -> optional author id; only books by this author are returned.
    book_ids   -> optional iterable restricting the result to these book ids.
    isbn       -> optional exact ISBN match (returns at most one book).
    """
    clauses = catalog_filters(
        genre=genre, author_id=author_id, book_ids=book_ids, isbn=isbn
    )
    return base_catalog_query().filter(*clauses).all()


def find_author_by_id(author_id):
    """Look up an author by id. None if not found."""
    return db.session.get(Author, author_id)


def find_genre_by_id(genre_id):
    """Look up a genre by id. None if not found."""
    return db.session.get(Genre, genre_id)


def create_book(fields):
    """Insert a new book row and link it to its author and genre.

    fields is the dict returned by validate_new_book_input, which includes
    author_id/genre_id alongside the Book columns. The book, its bookauthor
    link, and its book_genre link are all committed in one transaction, so a
    book is never left without an author or genre. Returns the created
    Book. Raises SQLAlchemyError if the commit fails (the caller is
    responsible for rollback).
    """
    link_ids = {"author_id": fields["author_id"], "genre_id": fields["genre_id"]}
    book_fields = {key: value for key, value in fields.items() if key not in link_ids}

    book = Book(**book_fields)
    db.session.add(book)
    db.session.flush()  # assigns book.id for the links below

    db.session.add(BookAuthor(book_id=book.id, author_id=link_ids["author_id"]))
    db.session.add(BookGenre(book_id=book.id, genre_id=link_ids["genre_id"]))
    db.session.commit()
    return book


def find_publisher_by_name(name):
    """Look up a publisher by name (case-insensitive). None if not found."""
    return Publisher.query.filter(
        func.lower(Publisher.name) == name.strip().lower()
    ).first()


def _books_for_publisher(publisher_id):
    """Books linked to a publisher through their authors.

        book -> bookauthor -> author -> publisher

    distinct() so a book with two matching authors is only returned once.
    """
    return (
        Book.query.join(BookAuthor, Book.id == BookAuthor.book_id)
        .join(Author, Author.id == BookAuthor.author_id)
        .filter(Author.publisher_id == publisher_id)
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
