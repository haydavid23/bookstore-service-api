from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from blueprints.book_catalog.service import (
    apply_publisher_discount,
    create_book,
    fetch_catalog_rows,
    find_author_by_id,
    find_genre_by_id,
    find_publisher_by_name,
    top_seller_counts,
)
from blueprints.book_catalog.utils import (
    filter_by_min_rating,
    serialize_book,
    sort_books,
    validate_discount_input,
    validate_new_book_input,
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
      author      -> only books by this author id
      min_rating  -> only books whose average review rating is >= this number
      sort        -> price_asc, price_desc, rating_desc, or top_sellers
    """
    genre = request.args.get("genre")
    author = request.args.get("author")
    min_rating = request.args.get("min_rating")
    sort = request.args.get("sort")

    if sort is not None and sort not in VALID_SORTS:
        return jsonify({"error": "Unsupported sort value."}), 400

    author_id = None
    if author is not None:
        try:
            author_id = int(author)
        except ValueError:
            return jsonify({"error": "author must be an integer id."}), 400

    sales_by_book_id = {}
    book_ids = None
    if sort == "top_sellers":
        sales_by_book_id = top_seller_counts()
        if not sales_by_book_id:
            return jsonify({"books": []}), 200
        book_ids = list(sales_by_book_id)

    rows = fetch_catalog_rows(genre=genre, author_id=author_id, book_ids=book_ids)
    books = [serialize_book(row) for row in rows]

    # Rating filter happens in Python because average_rating is a subquery value.
    if min_rating is not None:
        try:
            min_rating_value = float(min_rating)
        except ValueError:
            return jsonify({"error": "min_rating must be a number."}), 400
        books = filter_by_min_rating(books, min_rating_value)

    books = sort_books(books, sort, sales_by_book_id)

    return jsonify({"books": books})


@book_catalog_bp.route("/", methods=["POST"])
def create_book_route():
    """POST /book_catalog/ creates a new book.

    JSON body:
      isbn            -> string, required (max 250 chars)
      name            -> string, required (max 100 chars)
      description     -> string, optional (max 200 chars)
      price           -> number, required, >= 0
      year_published  -> number, required, >= 0
      copies_sold     -> number, optional, >= 0 (defaults to 0)
      author_id       -> integer, required, id of the book's author
      genre_id        -> integer, required, id of the book's genre
    """
    data = request.get_json(silent=True)
    fields, error = validate_new_book_input(data)
    if error:
        return jsonify({"error": error}), 400

    if fetch_catalog_rows(isbn=fields["isbn"]):
        return jsonify({"error": "A book with this ISBN already exists."}), 409

    author = find_author_by_id(fields["author_id"])
    if author is None:
        return jsonify({"error": "Author not found."}), 404

    genre = find_genre_by_id(fields["genre_id"])
    if genre is None:
        return jsonify({"error": "Genre not found."}), 404

    try:
        book = create_book(fields)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Failed to create book."}), 500

    response = book.to_dict()
    response["author"] = f"{author.name} {author.lastname}"
    response["genre"] = genre.genre

    return jsonify(response), 201


@book_catalog_bp.route("/isbn/<isbn>", methods=["GET"])
def get_book_by_isbn(isbn):
    """GET /book_catalog/isbn/<isbn> returns the single book with that ISBN.

    ISBN is unique, so this matches at most one book. Responds 404 when no book
    has the given ISBN.
    """
    rows = fetch_catalog_rows(isbn=isbn)
    if not rows:
        return jsonify({"error": "Book not found."}), 404

    return jsonify({"book": serialize_book(rows[0])})




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

    discount_value, error = validate_discount_input(publisher_name, discount_percent)
    if error:
        return jsonify({"error": error}), 400

    publisher = find_publisher_by_name(publisher_name)
    if publisher is None:
        return jsonify({"error": "Publisher not found."}), 404

    try:
        books_updated = apply_publisher_discount(publisher.id, discount_value)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Failed to apply discount."}), 500

    return (
        jsonify(
            {
                "publisher": publisher.name,
                "discount_percent": float(discount_value),
                "books_updated": books_updated,
            }
        ),
        200,
    )
