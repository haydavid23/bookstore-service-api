-- Seeds a handful of ratings and comments for book_id = 18, user_profile_id
-- = 18 (the test book/user from before), so GET /books/18/comments and
-- GET /books/18/ratings/average have real-looking data to return.
--
-- Adjust the ids below if you want to seed a different book/user.

INSERT INTO rating (book_id, user_profile_id, rating, created_at) VALUES
    (18, 18, 5, CURRENT_DATE - INTERVAL '3 days'),
    (18, 18, 3, CURRENT_DATE - INTERVAL '1 day'),
    (18, 18, 4, CURRENT_DATE);

-- Comments for book 18.
INSERT INTO comment (book_id, user_profile_id, comment, created_at) VALUES
    (18, 18, 'Couldn''t put it down.', CURRENT_DATE - INTERVAL '2 days'),
    (18, 18, 'A bit slow in the middle but worth it.', CURRENT_DATE - INTERVAL '1 day'),
    (18, 18, 'Would recommend to a friend.', CURRENT_DATE);
