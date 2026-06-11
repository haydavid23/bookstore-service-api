from flask import Blueprint, request, jsonify
from psycopg2.extras import RealDictCursor
import os
import psycopg2


profile_bp = Blueprint("profile", __name__)


def db_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


@profile_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    required_fields = [
        "username",
        "email",
        "first_name",
        "last_name",
        "password"
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    conn = db_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            INSERT INTO user_profile (
                username,
                email,
                address,
                first_name,
                last_name,
                password
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING
                id,
                username,
                email,
                address,
                first_name,
                last_name;
        """, (
            data["username"],
            data["email"],
            data.get("address"),
            data["first_name"],
            data["last_name"],
            data["password"]
        ))

        user = cur.fetchone()
        conn.commit()

        return jsonify(user), 201

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({
            "error": "Username or email already exists"
        }), 409

    finally:
        cur.close()
        conn.close()


@profile_bp.route("/users/<username>", methods=["GET"])
def get_user(username):
    conn = db_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            id,
            username,
            email,
            address,
            first_name,
            last_name
        FROM user_profile
        WHERE username = %s;
    """, (username,))

    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user), 200