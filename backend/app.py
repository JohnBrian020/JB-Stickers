import os
import hmac
import secrets

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from flask import (
    Flask,
    jsonify,
    request,
    session,
    make_response
)
from werkzeug.exceptions import RequestEntityTooLarge
from flask_cors import CORS

from config import Config
from extensions import db, migrate, bcrypt, limiter
from models import Product, Customer, Order, OrderItem, Admin
from routes.products import products_bp
from routes.orders import orders_bp
from routes.auth import auth_bp
from routes.admin import admin_bp
from utils.responses import error_response


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    limiter.init_app(app)

    allowed_origins = [
        origin.strip().rstrip("/")
        for origin in app.config.get(
            "FRONTEND_URL",
            "http://localhost:5173"
        ).split(",")
        if origin.strip()
    ]

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": allowed_origins
            }
        },
        supports_credentials=True,
        allow_headers=["Content-Type", "X-CSRFToken"]
    )

    @app.before_request
    def protect_api_requests():
        if not request.path.startswith("/api/"):
            return None

        if request.method in {"GET", "HEAD", "OPTIONS"}:
            return None

        # Reject browser requests originating from untrusted websites.
        origin = request.headers.get("Origin")

        if origin and origin.rstrip("/") not in allowed_origins:
            return error_response(
                "Request origin is not allowed",
                403
            )

        expected_token = session.get("csrf_token")
        supplied_token = request.headers.get("X-CSRFToken", "")

        if (
            not isinstance(expected_token, str)
            or not supplied_token
            or not hmac.compare_digest(
                expected_token,
                supplied_token
            )
        ):
            return error_response(
                "Invalid or missing CSRF token",
                403
            )

        return None
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "success",
            "message": "JB Stickers API is running"
        }), 200

    @app.errorhandler(429)
    def handle_rate_limit(error):
        return error_response(
            "Too many login attempts. Please try again later.",
            429
        )
    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(error):
        return error_response(
            "Uploaded file is too large. Maximum allowed size is 5 MB.",
            413
        )

    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        debug=app.config.get("APP_ENV") != "production",
        port=5000
    )