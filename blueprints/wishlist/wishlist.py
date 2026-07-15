from flask import Blueprint, request, jsonify
from extensions import db
from models.wishlist import WishList, WishItem

wishlist_bp = Blueprint('wishlist', __name__)

@wishlist_bp.route('/wishlist/items', methods=['GET'])
def get_wishlist_items():
    wish_list_id = request.args.get('wish_list_id')
    if not wish_list_id:
        return jsonify({"error": "wish_list_id is required"}), 400
    items = WishItem.query.filter_by(wish_list_id=wish_list_id).all()
    result = [item.to_dict() for item in items]
    return jsonify(result), 200

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

@wishlist_bp.route('/wishlist/user', methods=['GET'])
def get_wishlists_by_user():
    user_profile_id = request.args.get('user_profile_id')
    if not user_profile_id:
        return jsonify({"error": "user_profile_id is required"}), 400
    lists = WishList.query.filter_by(user_profile_id=user_profile_id).all()
    result = [wl.to_dict() for wl in lists]
    return jsonify(result), 200

@wishlist_bp.route('/wishlist/item', methods=['DELETE'])
def remove_item():
    data = request.get_json()
    if not data or 'wish_list_id' not in data or 'book_id' not in data:
        return jsonify({"error": "wish_list_id and book_id are required"}), 400
    item = WishItem.query.filter_by(
        wish_list_id=data['wish_list_id'],
        book_id=data['book_id']
    ).first()
    if not item:
        return jsonify({"error": "Item not found"}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Book removed from wishlist"}), 200

@wishlist_bp.route('/wishlist', methods=['DELETE'])
def delete_wishlist():
    data = request.get_json()
    if not data or 'wish_list_id' not in data:
        return jsonify({"error": "wish_list_id is required"}), 400
    wishlist = WishList.query.get(data['wish_list_id'])
    if not wishlist:
        return jsonify({"error": "Wishlist not found"}), 404
    db.session.delete(wishlist)
    db.session.commit()
    return jsonify({"message": "Wishlist deleted"}), 200
