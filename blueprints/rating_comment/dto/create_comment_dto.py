from dataclasses import dataclass
from datetime import date


# DTO for the POST /books/<book_id>/comments request body.
# Rubric parameters sent: Comment, User Id, Book Id.
# book_id comes from the URL path; comment and user_profile_id come from the
# JSON body. created_at is always stamped with today's date server-side.
@dataclass
class CreateCommentDTO:
    book_id: int
    user_profile_id: int
    comment: str
    created_at: date

    @classmethod
    def from_request(cls, data, book_id):
        """Build and validate a CreateCommentDTO from a JSON body.

        Returns a tuple of (dto, error). On success dto is set and error is
        None; on failure dto is None and error is a message string.
        """
        if not isinstance(data, dict):
            return None, "Invalid JSON body."

        # Validate user_profile_id.
        user_profile_id = data.get("user_profile_id")
        if not isinstance(user_profile_id, int) or isinstance(user_profile_id, bool):
            return None, "user_profile_id must be an integer."

        # Validate comment (required, max 100 chars).
        comment = data.get("comment")
        if not isinstance(comment, str) or not comment.strip():
            return None, "comment must be a non-empty string."
        if len(comment) > 100:
            return None, "comment must be at most 100 characters."

        dto = cls(
            book_id=book_id,
            user_profile_id=user_profile_id,
            comment=comment,
            created_at=date.today(),
        )
        return dto, None
