
from flask import Blueprint, request, session

from extensions import db
from models import Admin
from services.auth_service import authenticate_admin
from utils.responses import success_response, error_response


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_response("A valid JSON object is required")

    identifier = data.get("identifier")
    password = data.get("password")

    if not isinstance(identifier, str) or not identifier.strip():
        return error_response("Email or username is required")

    if not isinstance(password, str) or not password:
        return error_response("Password is required")

    admin = authenticate_admin(
        identifier.strip(),
        password
    )

    if admin is None:
        return error_response(
            "Invalid email, username or password",
            401
        )

    # Clear any previous session before creating a new one.
    session.clear()
    session["admin_id"] = admin.id
    session.permanent = True

    return success_response(
        data={
            "id": admin.id,
            "username": admin.username,
            "email": admin.email
        },
        message="Login successful"
    )


@auth_bp.route("/me", methods=["GET"])
def current_admin():

    admin_id = session.get("admin_id")

    if admin_id is None:
        return error_response("Authentication required", 401)

    admin = db.session.get(Admin, admin_id)

    if admin is None:
        session.clear()
        return error_response("Authentication required", 401)

    return success_response(
        data={
            "id": admin.id,
            "username": admin.username,
            "email": admin.email
        },
        message="Administrator session retrieved"
    )


@auth_bp.route("/logout", methods=["POST"])
def logout():

    session.clear()

    return success_response(
        message="Logout successful"
    )
