from extensions import db

# ShoppingCart model mapped to the "shopping_cart" table.
#   id              integer     NOT NULL    PK (autoincrement)
#   user_profile_id integer     NOT NULL    FK -> user_profile.id
#   updated_date    DATE        NULL

class ShoppingCart(db.Model):
    __tablename__ = "shopping_cart"

    __table_args__ = (
        db.UniqueConstraint("user_profile_id"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_profile_id = db.Column(
        db.Integer, db.ForeignKey("user_profile.id"), nullable=False
    )
    updated_date = db.Column(db.Date, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_profile_id": self.user_profile_id,
            "updated_date": self.updated_date.isoformat() if self.updated_date else None,
        }

    def __repr__(self):
        return (
            f"<ShoppingCart id={self.id} user_profile_id={self.user_profile_id}>"
        )
