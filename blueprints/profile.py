from flask import Blueprint, jsonify, request
from psycopg2.extras import RealDictCursor
from dtos.profile_dto import CreateProfileDTO, ProfileResponseDTO
import os
import psycopg2


profile_bp = Blueprint("profile", __name__)


def db_conn():
    """Open and return a connection to the configured PostgreSQL database."""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")

    return psycopg2.connect(database_url)


@profile_bp.route("/users", methods=["POST"])
def create_user():
    """Create a user profile from the submitted JSON request body."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be valid JSON"
        }), 400

    try:
        profile_dto = CreateProfileDTO.from_dict(data)
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
            profile_dto.username,
            profile_dto.email,
            profile_dto.address,
            profile_dto.first_name,
            profile_dto.last_name,
            profile_dto.password
        ))

        user_row = cur.fetchone()
        conn.commit()

        response_dto = ProfileResponseDTO.from_row(user_row)

        return jsonify(response_dto.to_dict()), 201

    except psycopg2.errors.UniqueViolation:
        if conn:
            conn.rollback()

        return jsonify({
            "error": "Username or email already exists"
        }), 409

    except psycopg2.Error:
        if conn:
            conn.rollback()

        return jsonify({
            "error": "Database error while creating user"
        }), 500

    finally:
        if cur:
            cur.close()

        if conn:
            conn.close()


@profile_bp.route("/users/<username>", methods=["GET"])
def get_user(username):
    """Retrieve one user profile by username."""
    conn = None
    cur = None

    try:
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

        user_row = cur.fetchone()

        if not user_row:
            return jsonify({
                "error": "User not found"
            }), 404

        response_dto = ProfileResponseDTO.from_row(user_row)

        return jsonify(response_dto.to_dict()), 200

    except psycopg2.Error:
        return jsonify({
            "error": "Database error while retrieving user"
        }), 500

    finally:
        if cur:
            cur.close()

        if conn:
            conn.close()