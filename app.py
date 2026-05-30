from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

from blueprints.bookdetails import bookdetails_bp

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

db = SQLAlchemy(app)

app.register_blueprint(bookdetails_bp)


@app.route("/")
def index():
    return jsonify({"message": "Welcome to BookDb"})


if __name__ == "__main__":
    app.run(debug=True)
