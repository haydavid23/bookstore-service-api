from dataclasses import dataclass


# DTO for a GET /authors response row.
# Shape matches the get_authors query output:
#   id         int   author id
#   name       str   author first name
#   lastname   str   author last name
#   bio        str   author biography
#   publisher  str   name of the publisher the author works with
@dataclass
class AuthorResponseDTO:
    id: int
    name: str
    lastname: str
    bio: str
    publisher: str

    @classmethod
    def from_row(cls, row):
        """Build an AuthorResponseDTO from a query result row."""
        return cls(
            id=row.id,
            name=row.name,
            lastname=row.lastname,
            bio=row.bio,
            publisher=row.publisher,
        )

    def to_dict(self):
        """Return a JSON-serializable dict of the author response."""
        return {
            "id": self.id,
            "name": self.name,
            "lastname": self.lastname,
            "bio": self.bio,
            "publisher": self.publisher,
        }
