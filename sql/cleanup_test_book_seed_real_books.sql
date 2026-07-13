-- Step 1: remove the throwaway "Test Book" (id 18) and anything that
-- references it. FK constraints mean the ratings/comments have to go first.
DELETE FROM rating WHERE book_id = 18;
DELETE FROM comment WHERE book_id = 18;
DELETE FROM book WHERE id = 18;

-- Step 2: seed ratings and comments against real catalog books instead,
-- still using the existing test user (id 18). Swap in whichever book ids
-- you want -- these match what's in the screenshot:
--   1 = The Pragmatic Programmer
--   5 = To Kill a Mockingbird
--   7 = Clean Code
--   9 = Harry Potter and the Deathly Hallows

INSERT INTO rating (book_id, user_profile_id, rating, created_at) VALUES
    (1, 18, 5, CURRENT_DATE - INTERVAL '5 days'),
    (5, 18, 4, CURRENT_DATE - INTERVAL '3 days'),
    (9, 18, 5, CURRENT_DATE - INTERVAL '2 days'),
    (7, 18, 3, CURRENT_DATE);

INSERT INTO comment (book_id, user_profile_id, comment, created_at) VALUES
    (1, 18, 'Changed how I think about writing code.', CURRENT_DATE - INTERVAL '5 days'),
    (5, 18, 'A classic for a reason.', CURRENT_DATE - INTERVAL '3 days'),
    (9, 18, 'Perfect ending to the series.', CURRENT_DATE - INTERVAL '2 days'),
    (7, 18, 'Solid principles, a bit repetitive.', CURRENT_DATE);
