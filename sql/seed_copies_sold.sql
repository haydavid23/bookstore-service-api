-- Seed varied copies_sold values so ?sort=top_sellers shows a real ranked top-10.
-- Idempotent: sets absolute values by book id, so re-running restores the same
-- ranking. Covers every seeded book (ids 1-12, 14, 15, 16). Note there is no id 13.
-- Values are distinct and spread roughly between 1,000 and 900,000.

UPDATE book SET copies_sold = 900000 WHERE id = 1;   -- The Pragmatic Programmer
UPDATE book SET copies_sold = 820000 WHERE id = 2;   -- Head First Design Patterns
UPDATE book SET copies_sold = 750000 WHERE id = 3;   -- Introduction to Algorithms
UPDATE book SET copies_sold = 680000 WHERE id = 4;   -- The Da Vinci Code
UPDATE book SET copies_sold = 610000 WHERE id = 5;   -- To Kill a Mockingbird
UPDATE book SET copies_sold = 540000 WHERE id = 6;   -- 1984
UPDATE book SET copies_sold = 470000 WHERE id = 7;   -- Clean Code
UPDATE book SET copies_sold = 400000 WHERE id = 8;   -- Designing Data-Intensive Applications
UPDATE book SET copies_sold = 330000 WHERE id = 9;   -- Harry Potter and the Deathly Hallows
UPDATE book SET copies_sold = 260000 WHERE id = 10;  -- The Lord of the Rings
UPDATE book SET copies_sold = 190000 WHERE id = 11;  -- Sapiens: A Brief History of Humankind
UPDATE book SET copies_sold = 120000 WHERE id = 12;  -- Thinking, Fast and Slow
UPDATE book SET copies_sold = 60000  WHERE id = 14;  -- Clean Architecture
UPDATE book SET copies_sold = 25000  WHERE id = 15;  -- Head First Design Patterns
UPDATE book SET copies_sold = 1000   WHERE id = 16;  -- Clean Code: A Handbook of Agile Software Craftsmanship
