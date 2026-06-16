from extensions import db


# OrderedItem model mapped to the "ordered_items" table.
# One row represents one purchased copy of a book.
# Column types and nullability mirror the database schema:
#   id              integer  NOT NULL  PK (autoincrement)
#   book_id         integer  NOT NULL  FK -> book.id
#   user_profile_id integer  NOT NULL  FK -> user_profile.id
#   order_date      date     NULL
class OrderedItem(db.Model):
    __tablename__ = "ordered_items"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    user_profile_id = db.Column(
        db.Integer, db.ForeignKey("user_profile.id"), nullable=False
    )
    order_date = db.Column(db.Date, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "book_id": self.book_id,
            "user_profile_id": self.user_profile_id,
            "order_date": self.order_date.isoformat() if self.order_date else None,
        }

    def __repr__(self):
        return (
            f"<OrderedItem id={self.id} book_id={self.book_id} "
            f"user_profile_id={self.user_profile_id}>"
        )
