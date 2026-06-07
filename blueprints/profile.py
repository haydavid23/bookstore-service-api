from flask import Blueprint, request, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor

profile_bp = Blueprint("profile", __name__)


def db_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def init_tables():
    conn = db_conn()
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


def get_user_row(username):
    conn = db_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, username, name, email, home_address
        FROM users
        WHERE username = %s;
    """, (username,))

    user = cur.fetchone()
    cur.close()
    conn.close()

    return user


@profile_bp.route("/users", methods=["POST"])
def create_user():
    init_tables()
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    conn = db_conn()
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
        return jsonify(user), 201

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({"error": "Username or email already exists"}), 409

    finally:
        cur.close()
        conn.close()


@profile_bp.route("/users/<username>", methods=["GET"])
def get_user(username):
    init_tables()
    user = get_user_row(username)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user), 200


@profile_bp.route("/users/<username>", methods=["PATCH"])
def update_user(username):
    init_tables()
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    if "email" in data or "mail" in data:
        return jsonify({"error": "Email cannot be updated"}), 400

    fields = []
    values = []

    for field in ["password", "name", "home_address"]:
        if field in data:
            fields.append(f"{field} = %s")
            values.append(data[field])

    if not fields:
        return jsonify({"error": "No valid update fields"}), 400

    values.append(username)

    conn = db_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(f"""
        UPDATE users
        SET {", ".join(fields)}
        WHERE username = %s
        RETURNING id, username, name, email, home_address;
    """, values)

    user = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user), 200


@profile_bp.route("/users/<username>/credit-cards", methods=["POST"])
def create_credit_card(username):
    init_tables()
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    for field in ["card_number", "expiration_month", "expiration_year", "cardholder_name"]:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    user = get_user_row(username)

    if not user:
        return jsonify({"error": "User not found"}), 404

    conn = db_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

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

    card = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()

    return jsonify(card), 201