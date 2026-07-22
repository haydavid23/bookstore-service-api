import os
from functools import wraps

import jwt
from flask import g, jsonify, request

def _get_token_payload():
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return None, (jsonify({"error": "Missing or invalid Authorization header"}), 401)

    token = auth_header.removeprefix("Bearer ").strip()

    if not token:
        return None, (jsonify({"error": "Missing token"}), 401)

    secret = os.getenv("JWT_SECRET_KEY")

    if not secret:
        return None, (jsonify({"error": "JWT secret is not configured"}), 500)

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None, (jsonify({"error": "Token has expired"}), 401)
    except jwt.InvalidTokenError:
        return None, (jsonify({"error": "Invalid token"}), 401)

    return payload, None

def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        payload, error_response = _get_token_payload()

        if error_response:
            return error_response

        g.current_user = payload

        return route_function(*args, **kwargs)

    return wrapper

def admin_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        payload, error_response = _get_token_payload()

        if error_response:
            return error_response

        g.current_user = payload

        if payload.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403

        return route_function(*args, **kwargs)

    return wrapper
