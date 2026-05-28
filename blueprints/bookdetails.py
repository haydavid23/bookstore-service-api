from flask import Blueprint

bookdetails_bp = Blueprint("bookdetails", __name__, url_prefix="/bookdetails")


@bookdetails_bp.route("/")
def index():
    return "bookdetails"
