from dataclasses import dataclass
from datetime import date


# DTO for the POST /books/<book_id>/ratings request body.
# Rubric parameters sent: Rating, User Id, Book Id.
# book_id comes from the URL path; rating and user_profile_id come from the
# JSON body. created_at is always stamped with today's date server-side.
@dataclass
class CreateRatingDTO:
    book_id: int
    user_profile_id: int
    rating: int
    created_at: date

    @classmethod
    def from_request(cls, data, book_id):
        """Build and validate a CreateRatingDTO from a JSON body.

        Returns a tuple of (dto, error). On success dto is set and error is
        None; on failure dto is None and error is a message string.
        """
        if not isinstance(data, dict):
            return None, "Invalid JSON body."

        # Validate user_profile_id.
        user_profile_id = data.get("user_profile_id")
        if not isinstance(user_profile_id, int) or isinstance(user_profile_id, bool):
            return None, "user_profile_id must be an integer."

        # Validate rating (1-5 star scale).
        rating = data.get("rating")
        if not isinstance(rating, int) or isinstance(rating, bool):
            return None, "rating must be an integer."
        if rating < 1 or rating > 5:
            return None, "rating must be between 1 and 5."

        dto = cls(
            book_id=book_id,
            user_profile_id=user_profile_id,
            rating=rating,
            created_at=date.today(),
        )
        return dto, None
