"""Database-backed validation for the author blueprint.

Pure-input validation (types, lengths) lives in the DTOs; checks that need a
database lookup live here so the route handlers in author.py stay thin.
"""

from extensions import db
from models import Publisher


def validate_publisher_id(publisher_id):
    """Check that a publisher with this id exists.

    Returns an error string, or None if the publisher exists.
    """
    if db.session.get(Publisher, publisher_id) is None:
        return "Publisher not found."

    return None
