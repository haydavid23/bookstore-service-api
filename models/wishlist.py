from extensions import db
from datetime import datetime

class WishList(db.Model):
    __tablename__ = "wish_list"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.Date, default=datetime.utcnow)
    user_profile_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'), nullable=False)

    items = db.relationship('WishItem', backref='wishlist', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": str(self.created_at),
            "user_profile_id": self.user_profile_id
        }

class WishItem(db.Model):
    __tablename__ = "wish_item"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    wish_list_id = db.Column(db.Integer, db.ForeignKey('wish_list.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "wish_list_id": self.wish_list_id,
            "book_id": self.book_id
        }