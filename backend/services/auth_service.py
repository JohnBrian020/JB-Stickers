
from extensions import bcrypt
from models import Admin


def authenticate_admin(identifier, password):
    """
    Authenticate an administrator using email or username.
    Return the Admin object if credentials are correct.
    Otherwise, return None.
    """

    admin = Admin.query.filter(
        (Admin.email == identifier) |
        (Admin.username == identifier)
    ).first()

    if admin is None:
        return None

    password_is_valid = bcrypt.check_password_hash(
        admin.password_hash,
        password
    )

    if not password_is_valid:
        return None

    return admin
