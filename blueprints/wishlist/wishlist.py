from flask import Blueprint, request, jsonify
from extensions import db
from models.wishlist import WishList, WishItem

wishlist_bp = Blueprint('wishlist', __name__)

# POST /wishlist
# Body: { "name": "My List", "user_profile_id": 1 }
@wishlist_bp.route('/wishlist', methods=['POST'])
def create_wishlist():
    data = request.get_json()

    if not data or 'name' not in data or 'user_profile_id' not in data:
        return jsonify({"error": "name and user_profile_id are required"}), 400

    new_list = WishList(
        name=data['name'],
        user_profile_id=data['user_profile_id']
    )

    db.session.add(new_list)
    db.session.commit()

    return jsonify({"message": "Wishlist created", "wishlist": new_list.to_dict()}), 201


# POST /wishlist/item
# Body: { "wish_list_id": 1, "book_id": 2 }
@wishlist_bp.route('/wishlist/item', methods=['POST'])
def add_item():
    data = request.get_json()

    if not data or 'wish_list_id' not in data or 'book_id' not in data:
        return jsonify({"error": "wish_list_id and book_id are required"}), 400

    new_item = WishItem(
        wish_list_id=data['wish_list_id'],
        book_id=data['book_id']
    )

    db.session.add(new_item)
    db.session.commit()

    return jsonify({"message": "Book added to wishlist", "item": new_item.to_dict()}), 201