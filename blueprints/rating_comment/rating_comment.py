from flask import Blueprint, g, jsonify, request
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from extensions import db
from auth import login_required
from models import Comment, Rating
from blueprints.rating_comment.dto.create_rating_dto import CreateRatingDTO
from blueprints.rating_comment.dto.create_comment_dto import CreateCommentDTO
from blueprints.rating_comment.dto.comment_response_dto import CommentResponseDTO


# Book Rating and Commenting blueprint.
# Every route here is scoped to a single book, so they're nested under
# /books/<book_id>/... . Ratings and comments are independent resources
# (separate tables, separate datestamps) rather than one combined "review",
# so a user can leave one without the other.
rating_comment_bp = Blueprint("rating_comment", __name__)


@rating_comment_bp.route("/books/<int:book_id>/ratings", methods=["POST"])
@login_required
def create_rating(book_id):
    """Create a 1-5 star rating for a book by a user, stamped with today's date.

    HTTP request type: POST
    Parameters sent: rating, user_profile_id (book_id comes from the path)
    Response data: none
    """
    dto, error = CreateRatingDTO.from_request(request.get_json(silent=True), book_id)
    if error:
        return jsonify({"error": error}), 400

    if (
        g.current_user["user_id"] != dto.user_profile_id
        and g.current_user["role"] != "admin"
    ):
        return jsonify({"error": "Cannot create a rating for another user"}), 403

    rating = Rating(
        book_id=dto.book_id,
        user_profile_id=dto.user_profile_id,
        rating=dto.rating,
        created_at=dto.created_at,
    )
    db.session.add(rating)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "book_id or user_profile_id does not exist."}), 404

    return "", 204


@rating_comment_bp.route("/books/<int:book_id>/comments", methods=["POST"])
@login_required
def create_comment(book_id):
    """Create a comment for a book by a user, stamped with today's date.

    HTTP request type: POST
    Parameters sent: comment, user_profile_id (book_id comes from the path)
    Response data: none
    """
    dto, error = CreateCommentDTO.from_request(request.get_json(silent=True), book_id)
    if error:
        return jsonify({"error": error}), 400

    if (
        g.current_user["user_id"] != dto.user_profile_id
        and g.current_user["role"] != "admin"
    ):
        return jsonify({"error": "Cannot create a comment for another user"}), 403

    comment = Comment(
        book_id=dto.book_id,
        user_profile_id=dto.user_profile_id,
        comment=dto.comment,
        created_at=dto.created_at,
    )
    db.session.add(comment)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "book_id or user_profile_id does not exist."}), 404

    return "", 204


@rating_comment_bp.route("/books/<int:book_id>/comments", methods=["GET"])
def list_comments(book_id):
    """Retrieve a list of all comments for a particular book.

    HTTP request type: GET
    Parameters sent: book_id (path)
    Response data: JSON list of comments
    """
    comments = (
        db.session.query(Comment)
        .filter(Comment.book_id == book_id)
        .order_by(Comment.created_at, Comment.id)
        .all()
    )

    return jsonify([CommentResponseDTO.from_model(c).to_dict() for c in comments])


@rating_comment_bp.route("/books/<int:book_id>/ratings/average", methods=["GET"])
def get_average_rating(book_id):
    """Retrieve the average rating for a book, computed as a decimal.

    HTTP request type: GET
    Parameters sent: book_id (path)
    Response data: computed average rating (decimal), null if unrated
    """
    average_rating = (
        db.session.query(func.avg(Rating.rating))
        .filter(Rating.book_id == book_id)
        .scalar()
    )

    return jsonify({
        "book_id": book_id,
        "average_rating": (
            round(float(average_rating), 2) if average_rating is not None else None
        ),
    })
