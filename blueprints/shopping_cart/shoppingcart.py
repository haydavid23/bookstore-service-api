from flask import g, Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from extensions import db
from auth import login_required
from models import UserProfile, ShoppingCart, CartItem, Book
shopping_cart_bp = Blueprint("shopping_cart", __name__)

@shopping_cart_bp.route("/users/<int:user_profile_id>/cart/subtotal", methods=["GET"])
@login_required
def retrieve_subtotal(user_profile_id):
   if g.current_user["user_id"] != user_profile_id and g.current_user["role"] != "admin":
       return jsonify({"error": "Cannot access another user's cart"}), 403
   user = UserProfile.query.get(user_profile_id)

   if not user:
       return jsonify({"error": "User not found"}), 404

   cart = ShoppingCart.query.filter_by(user_profile_id=user_profile_id).first()

   if cart is None:
       return jsonify({"user_profile_id": user_profile_id, "subtotal": 0}), 200

   subtotal = (
       db.session.query(db.func.sum(Book.price * CartItem.quantity))
       .select_from(CartItem)
       .join(Book, Book.id == CartItem.book_id)
       .filter(CartItem.shopping_cart_id == cart.id)
       .scalar()
   )

   return jsonify({
       "user_profile_id": user_profile_id,
       "subtotal": float(subtotal or 0)
   }), 200

@shopping_cart_bp.route("/users/<int:user_profile_id>/cart/items", methods=["POST"])
@login_required
def add_cart_item(user_profile_id):
    if (
        g.current_user["user_id"] != user_profile_id
        and g.current_user["role"] != "admin"
    ):
        return jsonify({"error": "Cannot access another user's cart"}), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON"}), 400

    book_id = data.get("book_id")
    quantity = data.get("quantity", 1)

    if not isinstance(book_id, int) or isinstance(book_id, bool):
        return jsonify({"error": "book_id must be an integer"}), 400

    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
        return jsonify({"error": "quantity must be a positive integer"}), 400

    user = UserProfile.query.get(user_profile_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    book = Book.query.get(book_id)

    if not book:
        return jsonify({"error": "Book not found"}), 404

    cart = ShoppingCart.query.filter_by(user_profile_id=user_profile_id).first()

    if cart is None:
        cart = ShoppingCart(user_profile_id=user_profile_id)
        db.session.add(cart)
        db.session.flush()

    item = CartItem.query.filter_by(
        shopping_cart_id=cart.id,
        book_id=book_id,
    ).first()

    if item:
        item.quantity += quantity
    else:
        item = CartItem(
            shopping_cart_id=cart.id,
            book_id=book_id,
            quantity=quantity,
        )
        db.session.add(item)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Book already exists in shopping cart"}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Database error while adding book to shopping cart"}), 500

    return jsonify({
        "message": "Book added to shopping cart",
        "cart_item": item.to_dict(),
    }), 201


    

@shopping_cart_bp.route("/users/<int:user_profile_id>/cart/items", methods=["GET"])
@login_required
def retrieve_cart_items(user_profile_id):
  if(g.current_user["user_id"] != user_profile_id and g.current_user["role"] != "admin"):
      return jsonify({"error": "Cannot access another user's cart"}), 403
  user = UserProfile.query.get(user_profile_id)

  if not user:
      return jsonify({"error": "User not found"}), 404

  cart = ShoppingCart.query.filter_by(user_profile_id=user_profile_id).first()

  if cart is None:
      return jsonify({
          "user_profile_id": user_profile_id,
          "books": []
      }), 200

  rows = (
      db.session.query(Book, CartItem.quantity)
      .join(CartItem, CartItem.book_id == Book.id)
      .filter(CartItem.shopping_cart_id == cart.id)
      .all()
  )

  books = []

  for book, quantity in rows:
      book_data = book.to_dict()
      book_data["quantity"] = quantity
      books.append(book_data)

  return jsonify({
      "user_profile_id": user_profile_id,
      "books": books
  }), 200


@shopping_cart_bp.route("/users/<int:user_profile_id>/cart/items/<int:book_id>", methods=["DELETE"])
@login_required
def delete_cart_item(user_profile_id, book_id):
  if(g.current_user["user_id"] != user_profile_id and g.current_user["role"] != "admin"):
      return jsonify({"error": "Cannot access another user's cart"}), 403

  user = UserProfile.query.get(user_profile_id)

  if not user:
      return jsonify({"error": "User not found"}), 404

  book = Book.query.get(book_id)

  if not book:
      return jsonify({"error": "Book not found"}), 404

  cart = ShoppingCart.query.filter_by(user_profile_id=user_profile_id).first()

  if cart is None:
      return jsonify({"error": "Shopping cart not found"}), 404

  item = CartItem.query.filter_by(
      shopping_cart_id=cart.id,
      book_id=book_id,
  ).first()

  if item is None:
      return jsonify({"error": "Book not found in shopping cart"}), 404

  db.session.delete(item)

  try:
      db.session.commit()
  except SQLAlchemyError:
      db.session.rollback()
      return jsonify({"error": "Database error while removing book from shopping cart"}), 500

  return jsonify({"message": "Book removed from shopping cart"}), 200
