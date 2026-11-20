
from functools import wraps

from flask import session

from extensions import db
from models import Admin
from utils.responses import error_response


def admin_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):
        admin_id = session.get("admin_id")

        if admin_id is None:
            return error_response(
                "Administrator authentication required",
                401
            )

        admin = db.session.get(Admin, admin_id)

        if (
            admin is None
            or session.get("session_version") != admin.session_version
        ):
            session.clear()

            return error_response(
                "Your administrator session has expired. Please log in again.",
                401
            )

        return function(*args, **kwargs)

    return decorated_function
