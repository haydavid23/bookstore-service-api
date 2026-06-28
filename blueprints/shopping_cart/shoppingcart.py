from flask import Blueprint, jsonify, request
from psycopg2.extras import RealDictCursor
import os
import psycopg2

shopping_cart_bp = Blueprint("shopping_cart", __name__)


def db_conn():
    """Open and return a connection to the configured PostgreSQL database."""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")

    return psycopg2.connect(database_url)


def require_int(data, field):
    value = data.get(field)

    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{field} must be an integer")

    return value


def serialize_book(row):
    return {
        "id": row["id"],
        "isbn": row["isbn"],
        "name": row["name"],
        "description": row["description"],
        "price": float(row["price"]) if row["price"] is not None else None,
        "year_published": (
            float(row["year_published"])
            if row["year_published"] is not None
            else None
        ),
    }


@shopping_cart_bp.route("/shopping-cart/items", methods=["POST"])
def add_book_to_cart():
    """Add a book to a user's shopping cart."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be valid JSON"
        }), 400

    try:
        book_id = require_int(data, "book_id")
        user_profile_id = require_int(data, "user_profile_id")
    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    conn = None
    cur = None

    try:
        conn = db_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            INSERT INTO ordered_items (
                book_id,
                user_profile_id,
                order_date
            )
            VALUES (%s, %s, NULL)
            RETURNING
                id,
                book_id,
                user_profile_id,
                order_date;
        """, (book_id, user_profile_id))

        cart_item = cur.fetchone()
        conn.commit()

        return jsonify({
            "message": "Book added to shopping cart",
            "cart_item": cart_item,
        }), 201

    except psycopg2.errors.ForeignKeyViolation:
        if conn:
            conn.rollback()

        return jsonify({
            "error": "book_id or user_profile_id does not exist"
        }), 404

    except psycopg2.Error:
        if conn:
            conn.rollback()

        return jsonify({
            "error": "Database error while adding book to shopping cart"
        }), 500

    finally:
        if cur:
            cur.close()

        if conn:
            conn.close()


@shopping_cart_bp.route(
    "/shopping-cart/users/<int:user_profile_id>/items",
    methods=["GET"],
)
def list_cart_books(user_profile_id):
    """Retrieve books currently in a user's shopping cart."""
    conn = None
    cur = None

    try:
        conn = db_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT 1
            FROM user_profile
            WHERE id = %s;
        """, (user_profile_id,))

        if not cur.fetchone():
            return jsonify({
                "error": "User not found"
            }), 404

        cur.execute("""
            SELECT
                b.id,
                b.isbn,
                b.name,
                b.description,
                b.price,
                b.year_published
            FROM ordered_items AS oi
            JOIN book AS b
                ON b.id = oi.book_id
            WHERE oi.user_profile_id = %s
                AND oi.order_date IS NULL
            ORDER BY oi.id;
        """, (user_profile_id,))

        books = [serialize_book(row) for row in cur.fetchall()]

        return jsonify({
            "user_profile_id": user_profile_id,
            "books": books,
        }), 200

    except psycopg2.Error:
        return jsonify({
            "error": "Database error while retrieving shopping cart"
        }), 500

    finally:
        if cur:
            cur.close()

        if conn:
            conn.close()
