from extensions import db


# UserProfile model mapped to the "user_profile" table.
# Column types and nullability mirror the UML diagram:
#   id         integer       NOT NULL  PK (autoincrement)
#   username   varchar(100)  NOT NULL  UNIQUE
#   email      varchar(100)  NOT NULL  UNIQUE
#   address    varchar(100)  NULL
#   first_name varchar(50)   NOT NULL
#   last_name  varchar(50)   NOT NULL
#   password   varchar(255)  NOT NULL  (stores a password hash, never plaintext)
#   role       text          NOT NULL
class UserProfile(db.Model):
    __tablename__ = "user_profile"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(100), nullable=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    # Stores a Werkzeug-generated password hash, never plaintext.
    # varchar(255) is wide enough for bcrypt (60 chars) and pbkdf2 hashes.
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Text, nullable=False)

    def to_dict(self):
        """Return a JSON-serializable dict — password hash is excluded."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "address": self.address,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role,
        }

    def __repr__(self):
        return f"<UserProfile id={self.id} username={self.username!r}>"
