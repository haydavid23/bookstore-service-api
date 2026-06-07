from flask_sqlalchemy import SQLAlchemy

# Shared SQLAlchemy instance.
# Defined here (not in app.py) so models can import `db` without a circular
# import. app.py binds it to the Flask app with db.init_app(app).
db = SQLAlchemy()
