from dataclasses import dataclass
from datetime import date


# DTO for one entry in the GET /books/<book_id>/comments response list.
@dataclass
class CommentResponseDTO:
    id: int
    book_id: int
    user_profile_id: int
    comment: str
    created_at: date | None

    @classmethod
    def from_model(cls, comment):
        """Build a CommentResponseDTO from a Comment ORM instance."""
        return cls(
            id=comment.id,
            book_id=comment.book_id,
            user_profile_id=comment.user_profile_id,
            comment=comment.comment,
            created_at=comment.created_at,
        )

    def to_dict(self):
        """Return a JSON-serializable dict of the comment."""
        return {
            "id": self.id,
            "book_id": self.book_id,
            "user_profile_id": self.user_profile_id,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
