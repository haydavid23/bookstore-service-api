from dataclasses import dataclass


# DTO for a GET /authors response row.
# Shape matches the get_authors query output:
#   id          int   author id
#   name        str   author first name
#   lastname    str   author last name
#   publishers  str   publisher names joined with ", " (STRING_AGG)
@dataclass
class AuthorResponseDTO:
    id: int
    name: str
    lastname: str
    publishers: str

    @classmethod
    def from_row(cls, row):
        """Build an AuthorResponseDTO from a query result row."""
        return cls(
            id=row.id,
            name=row.name,
            lastname=row.lastname,
            publishers=row.publishers,
        )

    def to_dict(self):
        """Return a JSON-serializable dict of the author response."""
        return {
            "id": self.id,
            "name": self.name,
            "lastname": self.lastname,
            "publishers": self.publishers,
        }
