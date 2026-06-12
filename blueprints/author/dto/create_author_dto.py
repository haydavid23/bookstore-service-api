from dataclasses import dataclass


# DTO for the POST /authors request body.
# Field constraints mirror the "author" table varchar sizes, plus the
# publisher the author works with (author.publisher_id, NOT NULL):
#   name          string  max 100 chars
#   lastname      string  max 100 chars
#   bio           string  max 150 chars
#   publisher_id  int     id of the publisher the author works with
@dataclass
class CreateAuthorDTO:
    name: str
    lastname: str
    bio: str
    publisher_id: int

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

        # Validate publisher_id as an integer (reject bools).
        publisher_id = data.get("publisher_id")
        if not isinstance(publisher_id, int) or isinstance(publisher_id, bool):
            return None, "publisher_id must be an integer."

        dto = cls(
            name=data["name"],
            lastname=data["lastname"],
            bio=data["bio"],
            publisher_id=publisher_id,
        )
        return dto, None

    def to_dict(self):
        """Return a JSON-serializable dict of the DTO."""
        return {
            "name": self.name,
            "lastname": self.lastname,
            "bio": self.bio,
            "publisher_id": self.publisher_id,
        }
