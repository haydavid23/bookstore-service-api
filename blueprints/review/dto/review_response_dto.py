from dataclasses import dataclass
from datetime import date


# DTO for a review response.
# Shape matches the review table columns (password excluded):
#   id              int
#   book_id         int
#   user_profile_id int
#   rating          int
#   comment         str | None
#   created_at      date | None
@dataclass
class ReviewResponseDTO:
    id: int
    book_id: int
    user_profile_id: int
    rating: int
    comment: str | None
    created_at: date | None

    @classmethod
    def from_model(cls, review):
        """Build a ReviewResponseDTO from a Review ORM instance."""
        return cls(
            id=review.id,
            book_id=review.book_id,
            user_profile_id=review.user_profile_id,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at,
        )

    def to_dict(self):
        """Return a JSON-serializable dict of the review response."""
        return {
            "id": self.id,
            "book_id": self.book_id,
            "user_profile_id": self.user_profile_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
