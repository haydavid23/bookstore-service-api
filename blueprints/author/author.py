from flask import Blueprint, jsonify, request

from auth import login_required
from extensions import db
from models import Author, Publisher
from blueprints.author.dto.create_author_dto import CreateAuthorDTO
from blueprints.author.dto.author_response_dto import AuthorResponseDTO
from blueprints.author.validators import validate_publisher_id


# Author Blueprint
# The url_prefix means the main route for this file is /authors.
author_bp = Blueprint("author", __name__, url_prefix="/authors")


# Required fields for creating an author. They mirror the NOT NULL columns
# on the "author" table: name, lastname, and bio.
REQUIRED_FIELDS = ["name", "lastname", "bio"]

# Max lengths mirror the varchar sizes in the database schema so we reject
# over-long values before they reach Postgres.
MAX_LENGTHS = {"name": 100, "lastname": 100, "bio": 150}



def validate_author_fields(data, partial=False):
    """Validate author input. Returns an error string, or None if valid.

    When partial is False (create) all REQUIRED_FIELDS must be present.
    When partial is True (update) only the provided fields are checked.
    """
    for field in REQUIRED_FIELDS:
        if field in data:
            value = data[field]
            if not isinstance(value, str) or not value.strip():
                return f"{field} must be a non-empty string."
            if len(value) > MAX_LENGTHS[field]:
                return f"{field} must be at most {MAX_LENGTHS[field]} characters."
        elif not partial:
            return f"{field} is required."

    return None


@author_bp.route("/", methods=["GET"])
def get_authors():
    """GET /authors returns each author with the name of their publisher.

    Mirrors:
      SELECT a.id, a.name, a.lastname, a.bio, p.name AS publisher
      FROM author a
        JOIN publisher p ON p.id = a.publisher_id;
    """
    rows = (
        db.session.query(
            Author.id,
            Author.name,
            Author.lastname,
            Author.bio,
            Publisher.name.label("publisher"),
        )
        .join(Publisher, Publisher.id == Author.publisher_id)
        .all()
    )

    authors = [AuthorResponseDTO.from_row(row).to_dict() for row in rows]

    return jsonify({"authors": authors})


@author_bp.route("/<int:author_id>", methods=["GET"])
def get_author(author_id):
    """GET /authors/<id> returns a single author with the name of their
    publisher (same shape as GET /authors)."""
    row = (
        db.session.query(
            Author.id,
            Author.name,
            Author.lastname,
            Author.bio,
            Publisher.name.label("publisher"),
        )
        .join(Publisher, Publisher.id == Author.publisher_id)
        .filter(Author.id == author_id)
        .first()
    )

    if row is None:
        return jsonify({"error": "Author not found."}), 404

    return jsonify(AuthorResponseDTO.from_row(row).to_dict())


@author_bp.route("/", methods=["POST"])
@login_required
def create_author():
    """POST /authors creates an author with the publisher they work with."""
    dto, error = CreateAuthorDTO.from_request(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    error = validate_publisher_id(dto.publisher_id)
    if error:
        return jsonify({"error": error}), 404

    author = Author(
        name=dto.name,
        lastname=dto.lastname,
        bio=dto.bio,
        publisher_id=dto.publisher_id,
    )

    db.session.add(author)
    db.session.commit()

    return jsonify(author.to_dict()), 201


@author_bp.route("/<int:author_id>", methods=["PUT", "PATCH"])
def update_author(author_id):
    """PUT/PATCH /authors/<id> updates an existing author.

    PATCH allows a partial update; PUT requires all fields. Either way only
    the provided fields are written.
    """
    author = db.session.get(Author, author_id)

    if author is None:
        return jsonify({"error": "Author not found."}), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid JSON body."}), 400

    partial = request.method == "PATCH"
    error = validate_author_fields(data, partial=partial)
    if error:
        return jsonify({"error": error}), 400

    for field in REQUIRED_FIELDS:
        if field in data:
            setattr(author, field, data[field])

    db.session.commit()

    return jsonify(author.to_dict())


@author_bp.route("/<int:author_id>", methods=["DELETE"])
def delete_author(author_id):
    """DELETE /authors/<id> removes an author."""
    author = db.session.get(Author, author_id)

    if author is None:
        return jsonify({"error": "Author not found."}), 404

    db.session.delete(author)
    db.session.commit()

    return jsonify({"message": "Author deleted."})
