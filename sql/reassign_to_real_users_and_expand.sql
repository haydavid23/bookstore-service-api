-- Step 1: repoint the ratings/comments created earlier (under the
-- throwaway test user, id 18) onto real users instead of deleting them.
UPDATE rating  SET user_profile_id = 1  WHERE book_id = 1 AND user_profile_id = 18; -- alice
UPDATE rating  SET user_profile_id = 9  WHERE book_id = 5 AND user_profile_id = 18; -- demo_user_1
UPDATE rating  SET user_profile_id = 3  WHERE book_id = 9 AND user_profile_id = 18; -- carol
UPDATE rating  SET user_profile_id = 17 WHERE book_id = 7 AND user_profile_id = 18; -- demo_user4

UPDATE comment SET user_profile_id = 1  WHERE book_id = 1 AND user_profile_id = 18;
UPDATE comment SET user_profile_id = 9  WHERE book_id = 5 AND user_profile_id = 18;
UPDATE comment SET user_profile_id = 3  WHERE book_id = 9 AND user_profile_id = 18;
UPDATE comment SET user_profile_id = 17 WHERE book_id = 7 AND user_profile_id = 18;

-- Step 2: add 2 more ratings + 2 more comments per book (3 total each),
-- each from a different real user (alice=1, bob=2, carol=3,
-- nathan_sprint2_0611=4, demo_user_1=9, demo_user3=16, demo_user4=17).

INSERT INTO rating (book_id, user_profile_id, rating, created_at) VALUES
    (1, 2,  4, CURRENT_DATE - INTERVAL '4 days'),  -- The Pragmatic Programmer
    (1, 3,  5, CURRENT_DATE - INTERVAL '2 days'),
    (5, 4,  5, CURRENT_DATE - INTERVAL '2 days'),  -- To Kill a Mockingbird
    (5, 16, 3, CURRENT_DATE - INTERVAL '1 day'),
    (9, 9,  5, CURRENT_DATE - INTERVAL '3 days'),  -- Harry Potter and the Deathly Hallows
    (9, 4,  4, CURRENT_DATE - INTERVAL '1 day'),
    (7, 1,  4, CURRENT_DATE - INTERVAL '3 days'),  -- Clean Code
    (7, 2,  2, CURRENT_DATE - INTERVAL '1 day');

INSERT INTO comment (book_id, user_profile_id, comment, created_at) VALUES
    (1, 2,  'Every dev should read this early in their career.', CURRENT_DATE - INTERVAL '4 days'),
    (1, 3,  'Dense but worth the effort.', CURRENT_DATE - INTERVAL '2 days'),
    (5, 4,  'Still relevant decades later.', CURRENT_DATE - INTERVAL '2 days'),
    (5, 16, 'Good but a slow start.', CURRENT_DATE - INTERVAL '1 day'),
    (9, 9,  'Satisfying conclusion to the series.', CURRENT_DATE - INTERVAL '3 days'),
    (9, 4,  'The final battle was incredible.', CURRENT_DATE - INTERVAL '1 day'),
    (7, 1,  'Made me rethink how I name variables.', CURRENT_DATE - INTERVAL '3 days'),
    (7, 2,  'Some advice feels dated now.', CURRENT_DATE - INTERVAL '1 day');

-- Step 3: nothing references the test user anymore, so it can go.
-- (If this errors with a foreign key violation, something else still
-- references user id 18 -- check shopping cart / wishlist / credit_card /
-- ordered_item before forcing it.)
DELETE FROM user_profile WHERE id = 18;
