from extensions import db


# Genre model mapped to the "genre" table.
# Column types and nullability mirror the database schema:
#   id     integer       NOT NULL  default nextval('genre_id_seq')
#   genre  varchar(100)  NOT NULL
class Genre(db.Model):
    __tablename__ = "genre"

    # SERIAL-style primary key backed by genre_id_seq.
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    genre = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        """Return a JSON-serializable dict of the genre row."""
        return {
            "id": self.id,
            "genre": self.genre,
        }

    def __repr__(self):
        return f"<Genre id={self.id} genre={self.genre!r}>"
