from extensions import db


# BookAuthor model mapped to the "bookauthor" table.
# Join table linking books to authors (many-to-many).
# Column types and nullability mirror the database schema:
#   id         integer  NOT NULL  default nextval('bookauthor_id_seq')
#   book_id    integer  NOT NULL  -> book.id
#   author_id  integer  NOT NULL  -> author.id
class BookAuthor(db.Model):
    __tablename__ = "bookauthor"

    # SERIAL-style primary key backed by bookauthor_id_seq.
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)

    def to_dict(self):
        """Return a JSON-serializable dict of the bookauthor row."""
        return {
            "id": self.id,
            "book_id": self.book_id,
            "author_id": self.author_id,
        }

    def __repr__(self):
        return f"<BookAuthor id={self.id} book_id={self.book_id} author_id={self.author_id}>"
