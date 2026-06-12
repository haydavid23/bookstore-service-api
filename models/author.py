from extensions import db


# Author model mapped to the "author" table.
# Column types and nullability mirror the database schema:
#   id            integer       NOT NULL  default nextval('author_id_seq')
#   name          varchar(100)  NOT NULL
#   lastname      varchar(100)  NOT NULL
#   bio           varchar(150)  NOT NULL
#   publisher_id  integer       NOT NULL  -> publisher.id
class Author(db.Model):
    __tablename__ = "author"

    # SERIAL-style primary key backed by author_id_seq.
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.String(150), nullable=False)
    publisher_id = db.Column(db.Integer, db.ForeignKey("publisher.id"), nullable=False)

    def to_dict(self):
        """Return a JSON-serializable dict of the author row."""
        return {
            "id": self.id,
            "name": self.name,
            "lastname": self.lastname,
            "bio": self.bio,
            "publisher_id": self.publisher_id,
        }

    def __repr__(self):
        return f"<Author id={self.id} name={self.name!r} lastname={self.lastname!r}>"
