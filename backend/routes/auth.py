
import secrets

from flask import Blueprint, request, session, make_response
from marshmallow import ValidationError, validate

from extensions import db, limiter, bcrypt
from models import Admin
from services.auth_service import authenticate_admin
from utils.decorators import admin_required
from utils.responses import success_response, error_response


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


def get_admin_from_session():
    admin_id = session.get("admin_id")

    if admin_id is None:
        return None

    admin = db.session.get(Admin, admin_id)

    if (
        admin is None
        or session.get("session_version") != admin.session_version
    ):
        session.clear()
        return None

    return admin


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

    admin = authenticate_admin(identifier.strip(), password)

    if admin is None:
        return error_response(
            "Invalid email, username or password",
            401
        )

    session.clear()
    session["admin_id"] = admin.id
    session["session_version"] = admin.session_version
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
    admin = get_admin_from_session()

    if admin is None:
        return error_response("Authentication required", 401)

    return success_response(
        data={
            "id": admin.id,
            "username": admin.username,
            "email": admin.email
        },
        message="Administrator session retrieved"
    )


@auth_bp.route("/profile", methods=["PATCH"])
@limiter.limit("5 per minute")
@admin_required
def update_profile():
    admin = get_admin_from_session()

    if admin is None:
        return error_response("Authentication required", 401)

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_response("A valid JSON object is required")

    username = data.get("username")
    email = data.get("email")
    current_password = data.get("current_password")

    if not isinstance(current_password, str) or not current_password:
        return error_response("Current password is required")

    if not bcrypt.check_password_hash(
        admin.password_hash,
        current_password
    ):
        return error_response("Current password is incorrect", 401)

    if username is not None:
        if not isinstance(username, str):
            return error_response("Username must be text")

        username = username.strip()

        if len(username) < 2 or len(username) > 80:
            return error_response(
                "Username must contain between 2 and 80 characters"
            )

        existing_username = Admin.query.filter(
            Admin.username == username,
            Admin.id != admin.id
        ).first()

        if existing_username:
            return error_response("That username is already in use", 409)

        admin.username = username

    if email is not None:
        if not isinstance(email, str):
            return error_response("Email must be text")

        email = email.strip().lower()

        try:
            validate.Email()(email)
        except ValidationError:
            return error_response("Please enter a valid email address")

        if len(email) > 120:
            return error_response("Email must not exceed 120 characters")

        existing_email = Admin.query.filter(
            Admin.email == email,
            Admin.id != admin.id
        ).first()

        if existing_email:
            return error_response("That email address is already in use", 409)

        admin.email = email

    if username is None and email is None:
        return error_response("Provide a username or email to update")

    db.session.commit()

    return success_response(
        data={
            "id": admin.id,
            "username": admin.username,
            "email": admin.email
        },
        message="Account profile updated"
    )


@auth_bp.route("/password", methods=["PATCH"])
@limiter.limit("5 per minute")
@admin_required
def update_password():
    admin = get_admin_from_session()

    if admin is None:
        return error_response("Authentication required", 401)

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_response("A valid JSON object is required")

    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not isinstance(current_password, str) or not current_password:
        return error_response("Current password is required")

    if not isinstance(new_password, str):
        return error_response("New password is required")

    if not bcrypt.check_password_hash(
        admin.password_hash,
        current_password
    ):
        return error_response("Current password is incorrect", 401)

    if len(new_password) < 12 or len(new_password) > 128:
        return error_response(
            "New password must contain between 12 and 128 characters"
        )

    if new_password == current_password:
        return error_response(
            "New password must be different from your current password"
        )

    admin.password_hash = bcrypt.generate_password_hash(
        new_password
    ).decode("utf-8")

    # Revoke all sessions issued with the previous version.
    admin.session_version += 1
    db.session.commit()

    # End this browser's session and issue a fresh anonymous CSRF token.
    session.clear()
    session["csrf_token"] = secrets.token_urlsafe(32)

    return success_response(
        data={"csrf_token": session["csrf_token"]},
        message="Password updated. Please log in again."
    )


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    session["csrf_token"] = secrets.token_urlsafe(32)

    return success_response(
        data={"csrf_token": session["csrf_token"]},
        message="Logout successful"
    )
