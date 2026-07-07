from extensions import db


# Book model mapped to the "book" table.
# Column types and nullability mirror the database schema:
#   id              integer        NOT NULL  default nextval('book_id_seq')
#   isbn            varchar(250)   NOT NULL
#   name            varchar(100)   NOT NULL
#   description     varchar(200)   NULL
#   price           numeric        NOT NULL
#   year_published  numeric        NOT NULL
class Book(db.Model):
    __tablename__ = "book"

    # SERIAL-style primary key backed by book_id_seq.
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    price = db.Column(db.Numeric, nullable=False)
    year_published = db.Column(db.Numeric, nullable=False)
    copies_sold = db.Column(db.Numeric, nullable=False)

    def to_dict(self):
        """Return a JSON-serializable dict of the book row."""
        return {
            "id": self.id,
            "isbn": self.isbn,
            "name": self.name,
            "description": self.description,
            "price": float(self.price) if self.price is not None else None,
            "year_published": (
                float(self.year_published)
                if self.year_published is not None
                else None
            ),
        }

    def __repr__(self):
        return f"<Book id={self.id} name={self.name!r}>"
