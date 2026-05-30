from flask import Flask, request, jsonify

from blueprints.bookdetails import bookdetails_bp

app = Flask(__name__)
app.register_blueprint(bookdetails_bp)


@app.route("/")
def index():
    return jsonify({"message": "Welcome to BookDb"})




if __name__ == "__main__":
    app.run(debug=True)
