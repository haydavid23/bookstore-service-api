from flask import Blueprint


bookbrowsing_bp = Blueprint("bookbrowsing", __name__, url_prefix="/bookbrowsing")


@bookbrowsing_bp.route("/")
def index():
    return "bookbrowsing"
