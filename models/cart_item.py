from extensions import db

# CartItem model mapped to the "cart_item" table.
#   id                  integer     NOT NULL    PK (autoincrement)
#   shopping_cart_id    integer     NOT NULL    FK -> shopping_cart.id
#   book_id             integer     NOT NULL    FK -> book.id
#   quantity            integer     NOT NULL    

class CartItem(db.Model):
    __tablename__ = "cart_item"

    __table_args__ = (
        db.UniqueConstraint("book_id", "shopping_cart_id"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shopping_cart_id = db.Column(
        db.Integer, db.ForeignKey("shopping_cart.id"), nullable=False
    )
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "shopping_cart_id": self.shopping_cart_id,
            "book_id": self.book_id,
            "quantity": self.quantity,
        }

    def __repr__(self):
        return (
            f"<CartItem id={self.id} shopping_cart_id={self.shopping_cart_id} "
            f"book_id={self.book_id}>"
        )
