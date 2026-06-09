from extensions import db


# AuthorPublisher model mapped to the "author_publisher" table.
# Join table linking authors to publishers (many-to-many).
# Column types and nullability mirror the database schema:
#   id            integer  NOT NULL  default nextval('author_publisher_id_seq')
#   author_id     integer  NULL      -> author.id
#   publisher_id  integer  NULL
class AuthorPublisher(db.Model):
    __tablename__ = "author_publisher"

    # SERIAL-style primary key backed by author_publisher_id_seq.
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=True)
    publisher_id = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        """Return a JSON-serializable dict of the author_publisher row."""
        return {
            "id": self.id,
            "author_id": self.author_id,
            "publisher_id": self.publisher_id,
        }

    def __repr__(self):
        return (
            f"<AuthorPublisher id={self.id} author_id={self.author_id} "
            f"publisher_id={self.publisher_id}>"
        )
