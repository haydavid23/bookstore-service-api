from dataclasses import dataclass
from datetime import date


# DTO for the POST /reviews request body.
# Field constraints mirror the "review" table:
#   book_id         int   NOT NULL  FK -> book.id
#   user_profile_id int   NOT NULL  FK -> user_profile.id
#   rating          int   NOT NULL  CHECK (1 <= rating <= 5)
#   comment         str   NULL      max 100 chars
#   created_at      date  NULL      defaults to today if omitted
@dataclass
class CreateReviewDTO:
    book_id: int
    user_profile_id: int
    rating: int
    comment: str | None
    created_at: date | None

    @classmethod
    def from_request(cls, data):
        """Build and validate a CreateReviewDTO from a JSON body.

        Returns a tuple of (dto, error). On success dto is set and error is
        None; on failure dto is None and error is a message string.
        """
        if not isinstance(data, dict):
            return None, "Invalid JSON body."

        # Validate book_id.
        book_id = data.get("book_id")
        if not isinstance(book_id, int) or isinstance(book_id, bool):
            return None, "book_id must be an integer."

        # Validate user_profile_id.
        user_profile_id = data.get("user_profile_id")
        if not isinstance(user_profile_id, int) or isinstance(user_profile_id, bool):
            return None, "user_profile_id must be an integer."

        # Validate rating (1-5).
        rating = data.get("rating")
        if not isinstance(rating, int) or isinstance(rating, bool):
            return None, "rating must be an integer."
        if rating < 1 or rating > 5:
            return None, "rating must be between 1 and 5."

        # Validate comment (max 100 chars).
        comment = data.get("comment")
        if comment is not None:
            if not isinstance(comment, str):
                return None, "comment must be a string."
            if len(comment) > 100:
                return None, "comment must be at most 100 characters."

        # Validate created_at (ISO date string).
        created_at_raw = data.get("created_at")
        created_at = None
        if created_at_raw is not None:
            try:
                created_at = date.fromisoformat(created_at_raw)
            except (ValueError, TypeError):
                return None, "created_at must be a valid ISO date string (YYYY-MM-DD)."

        dto = cls(
            book_id=book_id,
            user_profile_id=user_profile_id,
            rating=rating,
            comment=comment,
            created_at=created_at or date.today(),
        )
        return dto, None
