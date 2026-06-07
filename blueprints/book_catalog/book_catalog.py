from flask import Blueprint, jsonify, request

from extensions import db
from models import Book, Author, BookAuthor, Genre, BookGenre


# Book Browsing Blueprint
# The url_prefix means the main route for this file is /books.
book_catalog_bp = Blueprint("book_catalog", __name__, url_prefix="/book_catalog")


# Small mock book list for testing before connecting the database.
# Student note: this is temporary data. Later, these rows can come from the database or PostgreSQL instead.
MOCK_BOOKS = [
    {
        "id": 1,
        "ISBN": "9780143127741",
        "Name": "The Martian",
        "Description": "An astronaut must survive alone on Mars using science and creativity.",
        "Publisher_ID": 1,
        "price": 15.99,
        "year_published": 2014,
        "genre": "Science Fiction",
        "average_rating": 4.7,
    },
    {
        "id": 2,
        "ISBN": "9780061120084",
        "Name": "To Kill a Mockingbird",
        "Description": "A classic story about justice, childhood, and empathy.",
        "Publisher_ID": 2,
        "price": 12.99,
        "year_published": 1960,
        "genre": "Fiction",
        "average_rating": 4.8,
    },
    {
        "id": 3,
        "ISBN": "9780439708180",
        "Name": "Harry Potter and the Sorcerer's Stone",
        "Description": "A young wizard begins his first year at Hogwarts.",
        "Publisher_ID": 3,
        "price": 10.99,
        "year_published": 1997,
        "genre": "Fantasy",
        "average_rating": 4.6,
    },
    {
        "id": 4,
        "ISBN": "9780735211292",
        "Name": "Atomic Habits",
        "Description": "A practical guide to building better habits every day.",
        "Publisher_ID": 4,
        "price": 18.99,
        "year_published": 2018,
        "genre": "Self Help",
        "average_rating": 4.4,
    },
]


# Mock ordered items show which books were bought.
# Top sellers are counted from this list instead of a Book copies_sold field.
ORDERED_ITEMS = [
    {"book_id": 1, "quantity": 2},
    {"book_id": 2, "quantity": 5},
    {"book_id": 3, "quantity": 3},
    {"book_id": 2, "quantity": 1},
    {"book_id": 1, "quantity": 4},
]


VALID_SORTS = {"price_asc", "price_desc", "rating_desc", "top_sellers"}


def count_books_sold():
    """Add up mock ordered item quantities by book id."""
    totals = {}

    for item in ORDERED_ITEMS:
        book_id = item["book_id"]
        totals[book_id] = totals.get(book_id, 0) + item["quantity"]

    return totals


@book_catalog_bp.route("/", methods=["GET"])
def get_books():
    """GET /books returns mock books filtered and sorted by query parameters."""
    # request.args is the DTO from the user for this simple blueprint.
    genre = request.args.get("genre")
    min_rating = request.args.get("min_rating")
    sort = request.args.get("sort")

    # Query all books joined with their author and genre via the join tables.
    # Mirrors:
    #   SELECT b.id, b.isbn, b.name, b.description, b.price, b.year_published,
    #          a.name || ' ' || a.lastname AS author, g.genre
    #   FROM book b
    #     JOIN bookauthor ba ON b.id = ba.book_id
    #     JOIN author a      ON a.id = ba.author_id
    #     JOIN book_genre bg ON b.id = bg.book_id
    #     JOIN genre g       ON g.id = bg.genre_id
    rows = (
        db.session.query(
            Book.id,
            Book.isbn,
            Book.name,
            Book.description,
            Book.price,
            Book.year_published,
            (Author.name + " " + Author.lastname).label("author"),
            Genre.genre.label("genre"),
        )
        .join(BookAuthor, Book.id == BookAuthor.book_id)
        .join(Author, Author.id == BookAuthor.author_id)
        .join(BookGenre, Book.id == BookGenre.book_id)
        .join(Genre, Genre.id == BookGenre.genre_id)
        .all()
    )

    books = [
        {
            "id": row.id,
            "isbn": row.isbn,
            "name": row.name,
            "description": row.description,
            "price": float(row.price) if row.price is not None else None,
            "year_published": (
                float(row.year_published)
                if row.year_published is not None
                else None
            ),
            "author": row.author,
            "genre": row.genre,
        }
        for row in rows
    ]

    if genre:
        books = [book for book in books if book["genre"].lower() == genre.lower()]

    if min_rating is not None:
        try:
            min_rating_value = float(min_rating)
        except ValueError:
            return jsonify({"error": "min_rating must be a number."}), 400

        books = [
            book for book in books
            if book["average_rating"] >= min_rating_value
        ]

    if sort is not None:
        if sort not in VALID_SORTS:
            return jsonify({"error": "Unsupported sort value."}), 400

        if sort == "price_asc":
            books.sort(key=lambda book: book["price"])
        elif sort == "price_desc":
            books.sort(key=lambda book: book["price"], reverse=True)
        elif sort == "rating_desc":
            books.sort(key=lambda book: book["average_rating"], reverse=True)
        elif sort == "top_sellers":
            sold_totals = count_books_sold()

            for book in books:
                book["total_sold"] = sold_totals.get(book["id"], 0)

            books.sort(key=lambda book: book["total_sold"], reverse=True)

    return jsonify({"books": books})
