from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Review
from blueprints.review.dto.create_review_dto import CreateReviewDTO
from blueprints.review.dto.review_response_dto import ReviewResponseDTO


# Review Blueprint
# Base route: /reviews
review_bp = Blueprint("review", __name__, url_prefix="/reviews")

# Fields that may be updated via PATCH/PUT.
UPDATABLE_FIELDS = ["rating", "comment"]


def validate_update_fields(data, partial=False):
    """Validate update input. Returns an error string, or None if valid.

    When partial is False (PUT) at least one field must be present.
    When partial is True (PATCH) only provided fields are checked.
    """
    if not partial and not any(f in data for f in UPDATABLE_FIELDS):
        return "At least one of 'rating' or 'comment' must be provided."

    if "rating" in data:
        rating = data["rating"]
        if not isinstance(rating, int) or isinstance(rating, bool):
            return "rating must be an integer."
        if rating < 1 or rating > 5:
            return "rating must be between 1 and 5."

    if "comment" in data:
        comment = data["comment"]
        if comment is not None:
            if not isinstance(comment, str):
                return "comment must be a string."
            if len(comment) > 100:
                return "comment must be at most 100 characters."

    return None


@review_bp.route("/", methods=["GET"])
def get_reviews():
    """GET /reviews returns all reviews.

    Optional query param: ?book_id=<id> to filter by book.
    """
    book_id = request.args.get("book_id", type=int)

    query = db.session.query(Review)
    if book_id is not None:
        query = query.filter(Review.book_id == book_id)

    reviews = query.all()

    return jsonify({"reviews": [ReviewResponseDTO.from_model(r).to_dict() for r in reviews]})


@review_bp.route("/<int:review_id>", methods=["GET"])
def get_review(review_id):
    """GET /reviews/<id> returns a single review."""
    review = db.session.get(Review, review_id)

    if review is None:
        return jsonify({"error": "Review not found."}), 404

    return jsonify(ReviewResponseDTO.from_model(review).to_dict())


@review_bp.route("/", methods=["POST"])
def create_review():
    """POST /reviews creates a new review (rating + optional comment) for a book."""
    dto, error = CreateReviewDTO.from_request(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    review = Review(
        book_id=dto.book_id,
        user_profile_id=dto.user_profile_id,
        rating=dto.rating,
        comment=dto.comment,
        created_at=dto.created_at,
    )

    db.session.add(review)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "book_id or user_profile_id does not exist."}), 404

    return jsonify(ReviewResponseDTO.from_model(review).to_dict()), 201


@review_bp.route("/<int:review_id>", methods=["PUT", "PATCH"])
def update_review(review_id):
    """PUT/PATCH /reviews/<id> updates an existing review.

    PATCH allows partial update (only provided fields change).
    PUT expects at least one of rating or comment.
    """
    review = db.session.get(Review, review_id)

    if review is None:
        return jsonify({"error": "Review not found."}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body."}), 400

    partial = request.method == "PATCH"
    error = validate_update_fields(data, partial=partial)
    if error:
        return jsonify({"error": error}), 400

    for field in UPDATABLE_FIELDS:
        if field in data:
            setattr(review, field, data[field])

    db.session.commit()

    return jsonify(ReviewResponseDTO.from_model(review).to_dict())


@review_bp.route("/<int:review_id>", methods=["DELETE"])
def delete_review(review_id):
    """DELETE /reviews/<id> removes a review."""
    review = db.session.get(Review, review_id)

    if review is None:
        return jsonify({"error": "Review not found."}), 404

    db.session.delete(review)
    db.session.commit()

    return jsonify({"message": "Review deleted."})
