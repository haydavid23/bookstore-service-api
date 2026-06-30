"""Smoke tests for Kirneill's book catalog endpoints.

These tests use the configured DATABASE_URL, so run them with the same .env used
for local API testing.
"""

import unittest

from app import app


class BookCatalogSmokeTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_book_catalog_returns_unique_books(self):
        response = self.client.get("/book_catalog/")
        body = response.get_json()
        books = body["books"]
        book_ids = [book["id"] for book in books]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(book_ids), len(set(book_ids)))

    def test_book_catalog_filters_by_genre(self):
        response = self.client.get(
            "/book_catalog/?genre=Technology%20/%20Computer%20Science"
        )
        books = response.get_json()["books"]

        self.assertEqual(response.status_code, 200)
        self.assertTrue(books)
        self.assertTrue(
            all("Technology / Computer Science" in book["genre"] for book in books)
        )

    def test_book_catalog_filters_by_min_rating(self):
        response = self.client.get("/book_catalog/?min_rating=4")
        books = response.get_json()["books"]

        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(book["average_rating"] is not None for book in books))
        self.assertTrue(all(book["average_rating"] >= 4 for book in books))

    def test_book_catalog_sorts_top_sellers(self):
        response = self.client.get("/book_catalog/?sort=top_sellers")
        books = response.get_json()["books"]
        totals = [book["total_sold"] for book in books]

        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(books), 10)
        self.assertEqual(totals, sorted(totals, reverse=True))

    def test_book_catalog_rejects_invalid_sort(self):
        response = self.client.get("/book_catalog/?sort=bad")
        body = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", body)


if __name__ == "__main__":
    unittest.main()
