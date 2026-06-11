"""
Inserts sample users, books, and reviews with ratings.

Run once:
    python seed_reviews.py

Safe to re-run — skips each section if data already exists.
"""

from app import app
from extensions import db
from models.user_profile import UserProfile
from models.book import Book
from models.review import Review
from datetime import date
from werkzeug.security import generate_password_hash


SAMPLE_USERS = [
    {"username": "alice", "email": "alice@example.com", "first_name": "Alice", "last_name": "Smith", "address": "123 Maple St, New York, NY", "password": generate_password_hash("password1")},
    {"username": "bob", "email": "bob@example.com", "first_name": "Bob", "last_name": "Jones", "address": "456 Oak Ave, Los Angeles, CA", "password": generate_password_hash("password2")},
    {"username": "carol", "email": "carol@example.com", "first_name": "Carol", "last_name": "White", "address": "789 Pine Rd, Chicago, IL", "password": generate_password_hash("password3")},
]

SAMPLE_BOOKS = [
    {"isbn": "9780143127741", "name": "The Martian", "description": "Survival on Mars.", "price": 15.99, "year_published": 2014},
    {"isbn": "9780061120084", "name": "To Kill a Mockingbird", "description": "Justice and empathy.", "price": 12.99, "year_published": 1960},
    {"isbn": "9780439708180", "name": "Harry Potter and the Sorcerer's Stone", "description": "A boy discovers he is a wizard.", "price": 10.99, "year_published": 1997},
    {"isbn": "9780735211292", "name": "Atomic Habits", "description": "Building better habits.", "price": 18.99, "year_published": 2018},
    {"isbn": "9780062316097", "name": "The Alchemist", "description": "A journey of self-discovery.", "price": 14.99, "year_published": 1988},
]

SAMPLE_REVIEWS = [
    {"book_id": 1, "user_profile_id": 1, "rating": 5, "comment": "Absolutely loved it!", "created_at": date(2024, 1, 10)},
    {"book_id": 1, "user_profile_id": 2, "rating": 4, "comment": "Great read, highly recommend.", "created_at": date(2024, 2, 3)},
    {"book_id": 1, "user_profile_id": 3, "rating": 3, "comment": "A bit slow in the middle.", "created_at": date(2024, 3, 15)},
    {"book_id": 2, "user_profile_id": 1, "rating": 5, "comment": "A timeless classic.", "created_at": date(2024, 1, 20)},
    {"book_id": 2, "user_profile_id": 3, "rating": 4, "comment": "Very well written.", "created_at": date(2024, 4, 5)},
    {"book_id": 3, "user_profile_id": 2, "rating": 2, "comment": "Not really my genre.", "created_at": date(2024, 2, 28)},
    {"book_id": 3, "user_profile_id": 3, "rating": 5, "comment": "Couldn't put it down!", "created_at": date(2024, 5, 1)},
    {"book_id": 4, "user_profile_id": 1, "rating": 4, "comment": "Practical and insightful.", "created_at": date(2024, 3, 10)},
    {"book_id": 4, "user_profile_id": 2, "rating": 3, "comment": "Good but a bit repetitive.", "created_at": date(2024, 6, 7)},
    {"book_id": 5, "user_profile_id": 3, "rating": 5, "comment": "Changed the way I think.", "created_at": date(2024, 1, 30)},
]


def seed():
    with app.app_context():
        # Seed users
        if db.session.query(UserProfile).count() == 0:
            for data in SAMPLE_USERS:
                db.session.add(UserProfile(**data))
            db.session.commit()
            print(f"Seeded {len(SAMPLE_USERS)} users.")
        else:
            print("Users already exist, skipping.")

        # Seed books
        if db.session.query(Book).count() == 0:
            for data in SAMPLE_BOOKS:
                db.session.add(Book(**data))
            db.session.commit()
            print(f"Seeded {len(SAMPLE_BOOKS)} books.")
        else:
            print("Books already exist, skipping.")

        # Seed reviews
        if db.session.query(Review).count() == 0:
            for data in SAMPLE_REVIEWS:
                db.session.add(Review(**data))
            db.session.commit()
            print(f"Seeded {len(SAMPLE_REVIEWS)} reviews.")
        else:
            print("Reviews already exist, skipping.")


if __name__ == "__main__":
    seed()
