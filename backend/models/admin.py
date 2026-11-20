
from extensions import db


class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Incrementing this invalidates all previously issued admin sessions.
    session_version = db.Column(
        db.Integer,
        nullable=False,
        default=1,
        server_default="1"
    )

    def __repr__(self):
        return f"<Admin {self.username}>"
