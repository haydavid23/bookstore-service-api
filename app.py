from flask import Flask, jsonify
from dotenv import load_dotenv
import os

from extensions import db
from blueprints.book_catalog.book_catalog import book_catalog_bp
from blueprints.author.author import author_bp
from blueprints.profile import profile_bp
from blueprints.wishlist.wishlist import wishlist_bp
from blueprints.review.review import review_bp

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

db.init_app(app)

app.register_blueprint(book_catalog_bp)
app.register_blueprint(author_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(wishlist_bp)
app.register_blueprint(review_bp)


@app.route("/")
def index():
    return jsonify({"message": "Welcome to BookDb"})


if __name__ == "__main__":
    app.run(debug=True)
