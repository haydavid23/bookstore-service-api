from flask import Blueprint, request, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor


profile_bp = Blueprint("profile", __name__)


def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def create_tables_if_needed():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password VARCHAR(120) NOT NULL,
            name VARCHAR(120),
            email VARCHAR(120) UNIQUE,
            home_address VARCHAR(255)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS credit_cards (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            card_number VARCHAR(30) NOT NULL,
            expiration_month INTEGER NOT NULL,
            expiration_year INTEGER NOT NULL,
            cardholder_name VARCHAR(120) NOT NULL
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


@profile_bp.route("/users", methods=["POST"])
def create_user():
    create_tables_if_needed()

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username:
        return jsonify({"error": "Username is required"}), 400

    if not password:
        return jsonify({"error": "Password is required"}), 400

    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            INSERT INTO users (username, password, name, email, home_address)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, username, name, email, home_address;
        """, (
            username,
            password,
            data.get("name"),
            data.get("email"),
            data.get("home_address")
        ))

        user = cur.fetchone()
        conn.commit()

        return jsonify({
            "message": "User created successfully",
            "user": user
        }), 201

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({"error": "Username or email already exists"}), 409

    finally:
        cur.close()
        conn.close()


@profile_bp.route("/users/<username>", methods=["GET"])
def get_user(username):
    create_tables_if_needed()

    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, username, name, email, home_address
        FROM users
        WHERE username = %s;
    """, (username,))

    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user), 200


@profile_bp.route("/users/<username>", methods=["PATCH"])
def update_user(username):
    create_tables_if_needed()

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    if "email" in data or "mail" in data:
        return jsonify({"error": "Email/mail cannot be updated"}), 400

    allowed_fields = ["password", "name", "home_address"]
    updates = []
    values = []

    for field in allowed_fields:
        if field in data:
            updates.append(f"{field} = %s")
            values.append(data[field])

    if not updates:
        return jsonify({"error": "No valid fields provided for update"}), 400

    values.append(username)

    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    query = f"""
        UPDATE users
        SET {", ".join(updates)}
        WHERE username = %s
        RETURNING id, username, name, email, home_address;
    """

    cur.execute(query, values)
    user = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "message": "User updated successfully",
        "user": user
    }), 200


@profile_bp.route("/users/<username>/credit-cards", methods=["POST"])
def create_credit_card(username):
    create_tables_if_needed()

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    required_fields = [
        "card_number",
        "expiration_month",
        "expiration_year",
        "cardholder_name"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id
        FROM users
        WHERE username = %s;
    """, (username,))

    user = cur.fetchone()

    if not user:
        cur.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404

    cur.execute("""
        INSERT INTO credit_cards (
            user_id,
            card_number,
            expiration_month,
            expiration_year,
            cardholder_name
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, user_id, card_number, expiration_month, expiration_year, cardholder_name;
    """, (
        user["id"],
        data["card_number"],
        data["expiration_month"],
        data["expiration_year"],
        data["cardholder_name"]
    ))

    credit_card = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({
        "message": "Credit card created successfully",
        "credit_card": credit_card
    }), 201