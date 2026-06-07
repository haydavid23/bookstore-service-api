from extensions import db


# BookGenre model mapped to the "book_genre" table.
# Join table linking books to genres (many-to-many).
# Assumed schema (mirrors the bookauthor join table):
#   id        integer  NOT NULL  default nextval('book_genre_id_seq')
#   book_id   integer  NOT NULL  -> book.id
#   genre_id  integer  NOT NULL  -> genre.id
class BookGenre(db.Model):
    __tablename__ = "book_genre"

    # SERIAL-style primary key backed by book_genre_id_seq.
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"), nullable=False)

    def to_dict(self):
        """Return a JSON-serializable dict of the book_genre row."""
        return {
            "id": self.id,
            "book_id": self.book_id,
            "genre_id": self.genre_id,
        }

    def __repr__(self):
        return f"<BookGenre id={self.id} book_id={self.book_id} genre_id={self.genre_id}>"
