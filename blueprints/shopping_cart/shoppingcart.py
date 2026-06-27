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