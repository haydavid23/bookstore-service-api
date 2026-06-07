from flask import Blueprint, jsonify


# Book Browsing Blueprint
# David asked for the Sprint 2 version to stay simple for now.
# The url_prefix means every route in this file starts with /bookbrowsing.
bookbrowsing_bp = Blueprint("bookbrowsing", __name__, url_prefix="/bookbrowsing")


# Small mock book list for testing the blueprint before connecting the database.
# These keys match the updated Book table design from the database plan.
# Student note: this is temporary data. Later, these rows can come from MySQL instead.
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
    },
]


@bookbrowsing_bp.route("/", methods=["GET"])
def bookbrowsing_status():
    """GET /bookbrowsing/ confirms this blueprint is registered."""
    return jsonify({"message": "Book browsing blueprint is working."})


@bookbrowsing_bp.route("/books", methods=["GET"])
def get_mock_books():
    """GET /bookbrowsing/books returns the temporary mock book data."""
    return jsonify({"books": MOCK_BOOKS})
