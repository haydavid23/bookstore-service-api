from extensions import db


# Publisher model mapped to the "publisher" table.
# Only the columns used by the application are mapped here:
#   id    integer       NOT NULL  default nextval('publisher_id_seq')
#   name  varchar       NOT NULL
class Publisher(db.Model):
    __tablename__ = "publisher"

    # SERIAL-style primary key backed by publisher_id_seq.
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)

    def to_dict(self):
        """Return a JSON-serializable dict of the publisher row."""
        return {
            "id": self.id,
            "name": self.name,
        }

    def __repr__(self):
        return f"<Publisher id={self.id} name={self.name!r}>"
