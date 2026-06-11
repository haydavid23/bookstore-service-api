from sqlalchemy import CheckConstraint
from extensions import db


# Review model mapped to the "review" table.
# Column types and nullability mirror the UML diagram:
#   id              integer       NOT NULL  PK
#   book_id         integer       NOT NULL  FK -> book.id
#   user_profile_id integer       NOT NULL  FK -> user_profile.id
#   rating          integer       NOT NULL  CHECK (rating >= 1 AND rating <= 5)
#   comment         varchar(100)  NULL
#   created_at      date          NULL
class Review(db.Model):
    __tablename__ = "review"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    user_profile_id = db.Column(
        db.Integer, db.ForeignKey("user_profile.id"), nullable=False
    )
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.Date, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "book_id": self.book_id,
            "user_profile_id": self.user_profile_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return (
            f"<Review id={self.id} book_id={self.book_id} "
            f"user_profile_id={self.user_profile_id} rating={self.rating}>"
        )
