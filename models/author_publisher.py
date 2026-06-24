from extensions import db


# AuthorPublisher model mapped to the "author_publisher" table.
# Join table linking authors to publishers (many-to-many).
#   id            integer  NOT NULL  PK
#   author_id     integer  NOT NULL  -> author.id
#   publisher_id  integer  NOT NULL  -> publisher.id
class AuthorPublisher(db.Model):
    __tablename__ = "author_publisher"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)
    publisher_id = db.Column(db.Integer, db.ForeignKey("publisher.id"), nullable=False)

    def to_dict(self):
        """Return a JSON-serializable dict of the author_publisher row."""
        return {
            "id": self.id,
            "author_id": self.author_id,
            "publisher_id": self.publisher_id,
        }

    def __repr__(self):
        return (
            f"<AuthorPublisher id={self.id} "
            f"author_id={self.author_id} publisher_id={self.publisher_id}>"
        )
