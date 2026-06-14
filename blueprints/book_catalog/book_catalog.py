from flask import Blueprint, jsonify, request
from sqlalchemy import func

from extensions import db
from models import Book, Author, BookAuthor, Genre, BookGenre, Publisher, Review


# Book Browsing Blueprint
# url_prefix means every route in this file lives under /book_catalog.
book_catalog_bp = Blueprint("book_catalog", __name__, url_prefix="/book_catalog")


# Sort values the endpoint understands.
VALID_SORTS = {"price_asc", "price_desc", "rating_desc", "top_sellers"}


@book_catalog_bp.route("/", methods=["GET"])
def get_books():
    """GET /book_catalog/ returns live books, filtered and sorted by query params.

    Query params (all optional):
      genre       -> only books in this genre (case-insensitive)
      min_rating  -> only books whose average review rating is >= this number
      sort        -> price_asc, price_desc, rating_desc, or top_sellers
    """
    genre = request.args.get("genre")
    min_rating = request.args.get("min_rating")
    sort = request.args.get("sort")

    # Average review rating for one book. Correlated subquery so the author and
    # genre joins below can't inflate the count. NULL when a book has no reviews.
    avg_rating = (
        db.session.query(func.avg(Review.rating))
        .filter(Review.book_id == Book.id)
        .correlate(Book)
        .scalar_subquery()
    )

    # Join book -> author -> publisher and book -> genre.
    # Publisher comes from the author (author.publisher_id).
    query = (
        db.session.query(
            Book.id,
            Book.isbn,
            Book.name,
            Book.description,
            Book.price,
            Book.year_published,
            (Author.name + " " + Author.lastname).label("author"),
            Genre.genre.label("genre"),
            Publisher.name.label("publisher"),
            avg_rating.label("average_rating"),
        )
        .join(BookAuthor, Book.id == BookAuthor.book_id)
        .join(Author, Author.id == BookAuthor.author_id)
        .join(BookGenre, Book.id == BookGenre.book_id)
        .join(Genre, Genre.id == BookGenre.genre_id)
        .join(Publisher, Publisher.id == Author.publisher_id)
        # distinct() drops exact duplicate rows. A book with several authors or
        # genres can still appear once per author/genre (the join's nature).
        .distinct()
    )

    # Genre filter runs in the database (case-insensitive). Unknown genre -> no rows.
    if genre:
        query = query.filter(func.lower(Genre.genre) == genre.strip().lower())

    rows = query.all()

    books = [
        {
            "id": row.id,
            "isbn": row.isbn,
            "name": row.name,
            "description": row.description,
            "price": float(row.price) if row.price is not None else None,
            "year_published": (
                float(row.year_published) if row.year_published is not None else None
            ),
            "author": row.author,
            "genre": row.genre,
            "publisher": row.publisher,
            "average_rating": (
                round(float(row.average_rating), 2)
                if row.average_rating is not None
                else None
            ),
        }
        for row in rows
    ]

    # Rating filter: keep books whose average rating is >= the value.
    # Books with no reviews (None) can't meet a threshold, so they drop out.
    if min_rating is not None:
        try:
            min_rating_value = float(min_rating)
        except ValueError:
            return jsonify({"error": "min_rating must be a number."}), 400

        books = [
            book
            for book in books
            if book["average_rating"] is not None
            and book["average_rating"] >= min_rating_value
        ]

    if sort is not None:
        if sort not in VALID_SORTS:
            return jsonify({"error": "Unsupported sort value."}), 400

        if sort == "price_asc":
            books.sort(key=lambda book: book["price"])
        elif sort == "price_desc":
            books.sort(key=lambda book: book["price"], reverse=True)
        elif sort == "rating_desc":
            # Unrated books (None) sort to the bottom.
            books.sort(
                key=lambda book: (
                    book["average_rating"]
                    if book["average_rating"] is not None
                    else -1
                ),
                reverse=True,
            )
        elif sort == "top_sellers":
            # Needs the ordered_items table, which is not in the live DB yet.
            return (
                jsonify(
                    {"error": "Top sellers is not available until order data exists."}
                ),
                501,
            )

    return jsonify({"books": books})
