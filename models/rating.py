from sqlalchemy import CheckConstraint
from extensions import db


# Rating model mapped to the "rating" table.
# A single 1-5 star rating left by a user for a book, stamped with the date
# it was created. Split out from the old combined "review" table so a rating
# and a comment can be created independently, each with its own datestamp.
#   id              integer       NOT NULL  PK
#   book_id         integer       NOT NULL  FK -> book.id
#   user_profile_id integer       NOT NULL  FK -> user_profile.id
#   rating          integer       NOT NULL  CHECK (rating >= 1 AND rating <= 5)
#   created_at      date          NOT NULL
class Rating(db.Model):
    __tablename__ = "rating"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    user_profile_id = db.Column(
        db.Integer, db.ForeignKey("user_profile.id"), nullable=False
    )
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "book_id": self.book_id,
            "user_profile_id": self.user_profile_id,
            "rating": self.rating,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return (
            f"<Rating id={self.id} book_id={self.book_id} "
            f"user_profile_id={self.user_profile_id} rating={self.rating}>"
        )
