from flask import Blueprint, jsonify, request
from sqlalchemy import func

from extensions import db
from models import Author, AuthorPublisher, Publisher
from blueprints.author.dto.create_author_dto import CreateAuthorDTO
from blueprints.author.dto.author_response_dto import AuthorResponseDTO


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
    """GET /authors returns each author with their publishers joined into one
    comma-separated string.

    Mirrors:
      SELECT a.id, a.name, a.lastname, STRING_AGG(p.name, ', ') AS publishers
      FROM author a
        JOIN author_publisher ap ON a.id = ap.author_id
        JOIN publisher p         ON p.id = ap.publisher_id
      GROUP BY a.id, a.name, a.lastname;
    """
    rows = (
        db.session.query(
            Author.id,
            Author.name,
            Author.lastname,
            func.string_agg(Publisher.name, ", ").label("publishers"),
        )
        .join(AuthorPublisher, Author.id == AuthorPublisher.author_id)
        .join(Publisher, Publisher.id == AuthorPublisher.publisher_id)
        .group_by(Author.id, Author.name, Author.lastname)
        .all()
    )

    authors = [AuthorResponseDTO.from_row(row).to_dict() for row in rows]

    return jsonify({"authors": authors})


@author_bp.route("/<int:author_id>", methods=["GET"])
def get_author(author_id):
    """GET /authors/<id> returns a single author with their publishers joined
    into one comma-separated string (same shape as GET /authors).

    Uses an outer join so an existing author with no publisher links still
    returns (publishers is null); a 404 means the author id does not exist.
    """
    row = (
        db.session.query(
            Author.id,
            Author.name,
            Author.lastname,
            func.string_agg(Publisher.name, ", ").label("publishers"),
        )
        .outerjoin(AuthorPublisher, Author.id == AuthorPublisher.author_id)
        .outerjoin(Publisher, Publisher.id == AuthorPublisher.publisher_id)
        .filter(Author.id == author_id)
        .group_by(Author.id, Author.name, Author.lastname)
        .first()
    )

    if row is None:
        return jsonify({"error": "Author not found."}), 404

    return jsonify(AuthorResponseDTO.from_row(row).to_dict())


@author_bp.route("/", methods=["POST"])
def create_author():
    """POST /authors creates an author and links it to its publishers.

    The author row and the author_publisher join rows are written in a single
    transaction: flush the author to obtain its id, add a join row per
    publisher, then commit once so a failure can never orphan the author.
    """
    dto, error = CreateAuthorDTO.from_request(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    author = Author(
        name=dto.name,
        lastname=dto.lastname,
        bio=dto.bio,
    )

    db.session.add(author)
    # Flush (not commit) to assign author.id without ending the transaction.
    db.session.flush()

    for publisher_id in dto.publisher_ids:
        db.session.add(
            AuthorPublisher(author_id=author.id, publisher_id=publisher_id)
        )

    db.session.commit()

    result = author.to_dict()
    result["publisher_ids"] = dto.publisher_ids
    return jsonify(result), 201


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
