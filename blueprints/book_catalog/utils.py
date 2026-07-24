"""Pure helpers for the book catalog.

No Flask, request, or DB-session access here -- just serialization, input
validation, numeric math, and in-Python filtering/sorting so these functions
can be unit-tested in isolation.
"""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def serialize_book(row):
    """Turn a catalog query row into the JSON-serializable dict the API returns."""
    return {
        "id": row.id,
        "isbn": row.isbn,
        "name": row.name,
        "copies_sold": (
            int(row.copies_sold) if row.copies_sold is not None else None
        ),
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


def filter_by_min_rating(books, min_rating_value):
    """Keep books whose average rating is >= the threshold.

    Books with no reviews (None) can't meet a threshold, so they drop out.
    """
    return [
        book
        for book in books
        if book["average_rating"] is not None
        and book["average_rating"] >= min_rating_value
    ]


def sort_books(books, sort, sales_by_book_id):
    """Apply the requested ordering and return the resulting list.

    price_asc/price_desc/rating_desc sort in place; top_sellers de-dupes,
    attaches total_sold, sorts by it, and caps the list at 10.
    """
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
        return top_books[:10]

    return books


BOOK_MAX_LENGTHS = {"isbn": 250, "name": 100, "description": 200}


def _validate_non_negative_decimal(value, field_name):
    """Validate a required non-negative numeric field.

    Returns (Decimal, None) on success or (None, error_message) on failure.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        return None, f"{field_name} must be a number."
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None, f"{field_name} must be a number."
    if not decimal_value.is_finite():
        return None, f"{field_name} must be a number."
    if decimal_value < Decimal("0"):
        return None, f"{field_name} must be zero or greater."

    return decimal_value, None


def validate_new_book_input(data):
    """Validate the POST /book_catalog request body.

    Returns (fields, None) on success, where fields is a dict ready to
    construct a Book plus the author_id/genre_id to link it to, or (None,
    error_message) on failure. Required fields mirror the NOT NULL columns
    on the "book" table: isbn, name, price, and year_published, plus
    author_id (NOT NULL on bookauthor) and genre_id (NOT NULL on
    book_genre) -- every book needs an author and a genre. description is
    optional (nullable in the schema) and copies_sold defaults to 0 for a
    newly created book.
    """
    if not isinstance(data, dict):
        return None, "Invalid JSON body."

    for field in ("isbn", "name"):
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            return None, f"{field} must be a non-empty string."
        if len(value) > BOOK_MAX_LENGTHS[field]:
            return None, f"{field} must be at most {BOOK_MAX_LENGTHS[field]} characters."

    description = data.get("description")
    if description is not None:
        if not isinstance(description, str):
            return None, "description must be a string."
        if len(description) > BOOK_MAX_LENGTHS["description"]:
            return None, "description must be at most 200 characters."

    price, error = _validate_non_negative_decimal(data.get("price"), "price")
    if error:
        return None, error

    year_published, error = _validate_non_negative_decimal(
        data.get("year_published"), "year_published"
    )
    if error:
        return None, error

    copies_sold_input = data.get("copies_sold", 0)
    copies_sold, error = _validate_non_negative_decimal(copies_sold_input, "copies_sold")
    if error:
        return None, error

    author_id = data.get("author_id")
    if not isinstance(author_id, int) or isinstance(author_id, bool):
        return None, "author_id must be an integer."

    genre_id = data.get("genre_id")
    if not isinstance(genre_id, int) or isinstance(genre_id, bool):
        return None, "genre_id must be an integer."

    fields = {
        "isbn": data["isbn"],
        "name": data["name"],
        "description": description,
        "price": price,
        "year_published": year_published,
        "copies_sold": copies_sold,
        "author_id": author_id,
        "genre_id": genre_id,
    }
    return fields, None


def validate_discount_input(publisher_name, discount_percent):
    """Validate the discount request body.

    Returns (discount_value, None) on success or (None, error_message) on
    failure. discount_value is a finite Decimal between 0 and 100.
    """
    # Publisher name must be a non-empty string.
    if not isinstance(publisher_name, str) or not publisher_name.strip():
        return None, "publisher is required."

    # discount_percent must be a finite number between 0 and 100.
    if isinstance(discount_percent, bool):
        return None, "discount_percent must be a number."
    try:
        discount_value = Decimal(str(discount_percent))
    except (InvalidOperation, TypeError, ValueError):
        return None, "discount_percent must be a number."
    if not discount_value.is_finite():
        return None, "discount_percent must be a number."
    if discount_value < Decimal("0") or discount_value > Decimal("100"):
        return None, "discount_percent must be between 0 and 100."

    return discount_value, None


def compute_discounted_price(price, discount_value):
    """new price = price * (1 - percent/100), rounded to cents (half-up)."""
    multiplier = Decimal("1") - (discount_value / Decimal("100"))
    cents = Decimal("0.01")
    return (Decimal(str(price)) * multiplier).quantize(
        cents, rounding=ROUND_HALF_UP
    )
