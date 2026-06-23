"""WHERE-side query building for the book catalog.

Each catalog criterion becomes a SQLAlchemy clause; catalog_filters() collects
the active ones into a list the catalog query applies in one shot. To support a
new filter, add a single clause here -- the main query in service.py doesn't
change.
"""

from sqlalchemy import func

from extensions import db
from models import Book, BookAuthor, BookGenre, Genre


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


def catalog_filters(*, genre=None, author_id=None, book_ids=None, isbn=None):
    """Translate catalog criteria into a list of SQLAlchemy WHERE clauses.

    Only criteria that were supplied contribute a clause; the catalog query
    applies whatever comes back. Add a new filter by appending one clause here.

    genre      -> case-insensitive genre match.
    author_id  -> books written by this author id.
    book_ids   -> restrict to this iterable of book ids.
    isbn       -> exact ISBN match (returns at most one book).
    """
    clauses = []
    if book_ids is not None:
        clauses.append(Book.id.in_(book_ids))
    if genre:
        clauses.append(_genre_exists_filter(genre))
    if author_id is not None:
        clauses.append(_author_exists_filter(author_id))
    if isbn:
        clauses.append(Book.isbn == isbn.strip())
    return clauses
