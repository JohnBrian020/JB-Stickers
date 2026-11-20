import secrets

from flask import Blueprint, request, session, make_response

from extensions import db, limiter
from models import Admin
from services.auth_service import authenticate_admin
from utils.responses import success_response, error_response


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


@auth_bp.route("/csrf-token", methods=["GET"])
def get_csrf_token():
    token = session.get("csrf_token")

    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token

    response = make_response(
        success_response(
            data={"csrf_token": token},
            message="CSRF token retrieved"
        )
    )

    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"

    return response

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
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

    # Start a fresh authenticated session and rotate the CSRF token.
    session.clear()
    session["admin_id"] = admin.id
    session["csrf_token"] = secrets.token_urlsafe(32)
    session.permanent = True

    return success_response(
        data={
            "id": admin.id,
            "username": admin.username,
            "email": admin.email,
            "csrf_token": session["csrf_token"]
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

    # Create a fresh anonymous session with a new CSRF token.
    session["csrf_token"] = secrets.token_urlsafe(32)

    return success_response(
        data={"csrf_token": session["csrf_token"]},
        message="Logout successful"
    )