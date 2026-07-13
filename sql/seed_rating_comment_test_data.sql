-- Minimal seed data to test the rating/comment endpoints.
-- Inserts one book and one user, returning their ids so you can plug them
-- straight into the curl commands (POST /books/<book_id>/ratings, etc).
--
-- isbn/username/email use a random suffix so re-running this doesn't hit
-- the unique constraints if you already have seed data with similar values.

INSERT INTO book (isbn, name, description, price, year_published)
VALUES (
    'TEST-' || substr(md5(random()::text), 1, 10),
    'Test Book',
    'Seeded for API testing',
    19.99,
    2024
)
RETURNING id AS book_id;

INSERT INTO user_profile (username, email, first_name, last_name, password)
VALUES (
    'testuser_' || substr(md5(random()::text), 1, 8),
    'testuser_' || substr(md5(random()::text), 1, 8) || '@example.com',
    'Test',
    'User',
    'not-a-real-hash'
)
RETURNING id AS user_profile_id;
