from extensions import db


# Comment model mapped to the "comment" table.
# A single comment left by a user for a book, stamped with the date it was
# created. Split out from the old combined "review" table so a comment and a
# rating can be created independently, each with its own datestamp.
#   id              integer       NOT NULL  PK
#   book_id         integer       NOT NULL  FK -> book.id
#   user_profile_id integer       NOT NULL  FK -> user_profile.id
#   comment         varchar(100)  NOT NULL
#   created_at      date          NOT NULL
class Comment(db.Model):
    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    user_profile_id = db.Column(
        db.Integer, db.ForeignKey("user_profile.id"), nullable=False
    )
    comment = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "book_id": self.book_id,
            "user_profile_id": self.user_profile_id,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return (
            f"<Comment id={self.id} book_id={self.book_id} "
            f"user_profile_id={self.user_profile_id}>"
        )
