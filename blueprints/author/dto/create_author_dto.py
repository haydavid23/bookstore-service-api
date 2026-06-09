from dataclasses import dataclass


# DTO for the POST /authors request body.
# Field constraints mirror the "author" table varchar sizes, plus the list of
# publishers the author belongs to (many-to-many via author_publisher):
#   name           string      max 100 chars
#   lastname       string      max 100 chars
#   bio            string      max 150 chars
#   publisher_ids  list[int]   non-empty list of publisher ids to link to
@dataclass
class CreateAuthorDTO:
    name: str
    lastname: str
    bio: str
    publisher_ids: list

    # Max lengths mirror the varchar sizes in the database schema.
    MAX_LENGTHS = {"name": 100, "lastname": 100, "bio": 150}

    @classmethod
    def from_request(cls, data):
        """Build and validate a CreateAuthorDTO from a JSON body.

        Returns a tuple of (dto, error). On success dto is set and error is
        None; on failure dto is None and error is a message string.
        """
        if not isinstance(data, dict):
            return None, "Invalid JSON body."

        # Validate the string fields against type, emptiness, and max length.
        for name, max_len in cls.MAX_LENGTHS.items():
            value = data.get(name)
            if not isinstance(value, str) or not value.strip():
                return None, f"{name} must be a non-empty string."
            if len(value) > max_len:
                return None, f"{name} must be at most {max_len} characters."

        # Validate publisher_ids as a non-empty list of integers (reject bools).
        publisher_ids = data.get("publisher_ids")
        if not isinstance(publisher_ids, list) or not publisher_ids:
            return None, "publisher_ids must be a non-empty list of integers."
        for pid in publisher_ids:
            if not isinstance(pid, int) or isinstance(pid, bool):
                return None, "publisher_ids must be a non-empty list of integers."

        dto = cls(
            name=data["name"],
            lastname=data["lastname"],
            bio=data["bio"],
            publisher_ids=publisher_ids,
        )
        return dto, None

    def to_dict(self):
        """Return a JSON-serializable dict of the DTO."""
        return {
            "name": self.name,
            "lastname": self.lastname,
            "bio": self.bio,
            "publisher_ids": self.publisher_ids,
        }
