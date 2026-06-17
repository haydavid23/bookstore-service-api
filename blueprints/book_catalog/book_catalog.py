from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from flask import Blueprint, jsonify, request
from sqlalchemy import func, literal_column
from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy.exc import SQLAlchemyError

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

    if sort is not None and sort not in VALID_SORTS:
        return jsonify({"error": "Unsupported sort value."}), 400

    sales_by_book_id = {}
    if sort == "top_sellers":
        sold_count = func.count(OrderedItem.id)
        top_seller_rows = (
            db.session.query(
                OrderedItem.book_id,
                sold_count.label("total_sold"),
            )
            .group_by(OrderedItem.book_id)
            .order_by(sold_count.desc())
            .all()
        )
        if not top_seller_rows:
            return jsonify({"books": []}), 200

        sales_by_book_id = {
            row.book_id: int(row.total_sold) for row in top_seller_rows
        }

    # Average review rating for one book. Correlated subquery so the author and
    # genre joins below can't inflate the count. NULL when a book has no reviews.
    avg_rating = (
        db.session.query(func.avg(Review.rating))
        .filter(Review.book_id == Book.id)
        .correlate(Book)
        .scalar_subquery()
    )

    # Each book must come back as exactly ONE row, so authors, genres, and
    # publishers are pre-aggregated in their own subqueries (one row per
    # book_id) and LEFT JOINed onto book. Joining book_author and book_genre in
    # the same flat query would multiply the two sets together -- a 3-author,
    # 2-genre book would otherwise yield 6 rows with duplicated values.
    author_full_name = Author.name + " " + Author.lastname

    # Authors per book, combined alphabetically into a single field.
    authors_subq = (
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

    # Genres per book, combined alphabetically into a single field.
    genres_subq = (
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

    # Publishers per book via the author -> author_publisher mapping. Distinct
    # first (several of a book's authors can share one publisher), then combined
    # alphabetically so this aggregate is also one row per book.
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
    publishers_subq = (
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

    # LEFT JOIN each aggregate so books with no authors, genres, or publishers
    # are still returned (those fields come back NULL). Every subquery has one
    # row per book_id, so the joins stay one-to-one and nothing is duplicated.
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

    if sort == "top_sellers":
        query = query.filter(Book.id.in_(list(sales_by_book_id)))

    # Genre filter runs in the database (case-insensitive). EXISTS keeps each
    # book a single row instead of re-joining the genre table. Unknown genre -> no rows.
    if genre:
        genre_match = (
            db.session.query(BookGenre.book_id)
            .join(Genre, Genre.id == BookGenre.genre_id)
            .filter(BookGenre.book_id == Book.id)
            .filter(func.lower(Genre.genre) == genre.strip().lower())
            .exists()
        )
        query = query.filter(genre_match)

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
        top_books = []
        seen_book_ids = set()
        for book in books:
            book_id = book["id"]
            if book_id in seen_book_ids:
                continue
            seen_book_ids.add(book_id)
            book["total_sold"] = sales_by_book_id[book_id]
            top_books.append(book)

        top_books.sort(key=lambda book: book["total_sold"], reverse=True)
        books = top_books[:10]

    return jsonify({"books": books})


@book_catalog_bp.route("/discount", methods=["PATCH"])
def discount_by_publisher():
    """PATCH /book_catalog/discount lowers the price of every book from one publisher.

    JSON body:
      publisher         -> publisher name (required)
      discount_percent  -> number 0-100 (required), percent off each price
    """
    data = request.get_json(silent=True) or {}
    publisher_name = data.get("publisher")
    discount_percent = data.get("discount_percent")

    # Publisher name must be a non-empty string.
    if not isinstance(publisher_name, str) or not publisher_name.strip():
        return jsonify({"error": "publisher is required."}), 400

    # discount_percent must be a finite number between 0 and 100.
    if isinstance(discount_percent, bool):
        return jsonify({"error": "discount_percent must be a number."}), 400
    try:
        discount_value = Decimal(str(discount_percent))
    except (InvalidOperation, TypeError, ValueError):
        return jsonify({"error": "discount_percent must be a number."}), 400
    if not discount_value.is_finite():
        return jsonify({"error": "discount_percent must be a number."}), 400
    if discount_value < Decimal("0") or discount_value > Decimal("100"):
        return jsonify({"error": "discount_percent must be between 0 and 100."}), 400

    # Look up the publisher by name (case-insensitive).
    publisher = (
        Publisher.query.filter(
            func.lower(Publisher.name) == publisher_name.strip().lower()
        ).first()
    )
    if publisher is None:
        return jsonify({"error": "Publisher not found."}), 404

    # Books link to a publisher through their author:
    #   book -> bookauthor -> author_publisher -> publisher
    # distinct() so a book with two matching authors is only counted once.
    books = (
        Book.query.join(BookAuthor, Book.id == BookAuthor.book_id)
        .join(AuthorPublisher, AuthorPublisher.author_id == BookAuthor.author_id)
        .filter(AuthorPublisher.publisher_id == publisher.id)
        .distinct()
        .all()
    )

    # Apply the discount: new price = price * (1 - percent/100).
    multiplier = Decimal("1") - (discount_value / Decimal("100"))
    cents = Decimal("0.01")
    for book in books:
        if book.price is not None:
            book.price = (Decimal(str(book.price)) * multiplier).quantize(
                cents, rounding=ROUND_HALF_UP
            )

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Failed to apply discount."}), 500

    return (
        jsonify(
            {
                "publisher": publisher.name,
                "discount_percent": float(discount_value),
                "books_updated": len(books),
            }
        ),
        200,
    )
