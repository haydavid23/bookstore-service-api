from extensions import db


# CreditCard model mapped to the "credit_card" table.
# Column types and nullability mirror the UML diagram:
#   id              integer       NOT NULL  PK
#   card_number     varchar(100)  NOT NULL  UNIQUE
#   expiration_date date          NULL
#   user_profile_id integer       NOT NULL  FK -> user_profile.id
#   cvv             integer       NULL
class CreditCard(db.Model):
    __tablename__ = "credit_card"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_number = db.Column(db.String(100), unique=True, nullable=False)
    expiration_date = db.Column(db.Date, nullable=True)
    user_profile_id = db.Column(
        db.Integer, db.ForeignKey("user_profile.id"), nullable=False
    )
    cvv = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "card_number": self.card_number,
            "expiration_date": (
                self.expiration_date.isoformat() if self.expiration_date else None
            ),
            "user_profile_id": self.user_profile_id,
        }

    def __repr__(self):
        return f"<CreditCard id={self.id} user_profile_id={self.user_profile_id}>"
