-- Seeds 3 new books, each with one rating and one comment (from the
-- existing test user, id 18). Good for confirming ratings/comments stay
-- scoped to the right book_id and don't leak across books.
--
-- Everything chains off one statement so the new book ids come back at the
-- end without needing to copy ids between separate runs.

WITH new_books AS (
    INSERT INTO book (isbn, name, description, price, year_published)
    VALUES
        ('TEST-' || substr(md5(random()::text), 1, 10), 'Test Book B', 'Seeded for API testing', 14.99, 2022),
        ('TEST-' || substr(md5(random()::text), 1, 10), 'Test Book C', 'Seeded for API testing', 24.99, 2023),
        ('TEST-' || substr(md5(random()::text), 1, 10), 'Test Book D', 'Seeded for API testing', 9.99,  2021)
    RETURNING id, name
),
ranked AS (
    SELECT id, name, row_number() OVER () AS rn
    FROM new_books
),
new_ratings AS (
    INSERT INTO rating (book_id, user_profile_id, rating, created_at)
    SELECT id, 18, CASE rn WHEN 1 THEN 2 WHEN 2 THEN 5 ELSE 3 END, CURRENT_DATE
    FROM ranked
    RETURNING id
),
new_comments AS (
    INSERT INTO comment (book_id, user_profile_id, comment, created_at)
    SELECT id, 18, 'First impressions of ' || name, CURRENT_DATE
    FROM ranked
    RETURNING id
)
SELECT id AS book_id, name FROM ranked;
