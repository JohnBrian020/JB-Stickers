
import os
import secrets
from datetime import timedelta

class Config:
    APP_ENV = os.getenv("APP_ENV", "development").lower()

    # Production must always use a real, securely generated secret.
    _secret_key = os.getenv("SECRET_KEY")

    if APP_ENV == "production":
        if (
            not _secret_key
            or len(_secret_key) < 32
            or _secret_key == "replace-with-a-secure-random-secret"
        ):
            raise RuntimeError(
                "A secure SECRET_KEY of at least 32 characters "
                "must be configured in production."
            )

    SECRET_KEY = _secret_key or secrets.token_hex(32)

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///jb_stickers.db"
    )

    # Normalize older PostgreSQL URL formats.
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://",
            "postgresql://",
            1
        )

    # Production must use PostgreSQL.
    if APP_ENV == "production" and not SQLALCHEMY_DATABASE_URI.startswith(
        "postgresql://"
    ):
        raise RuntimeError(
            "A PostgreSQL DATABASE_URL must be configured in production."
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True

    SESSION_COOKIE_SAMESITE = os.getenv(
        "SESSION_COOKIE_SAMESITE",
        "None" if APP_ENV == "production" else "Lax"
    )

    SESSION_COOKIE_SECURE = (
        APP_ENV == "production"
        or os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    )

    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # Resend email configuration
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")

    MAIL_FROM = os.getenv(
        "MAIL_FROM",
        "onboarding@resend.dev"
    )

    FRONTEND_URL = os.getenv(
        "FRONTEND_URL",
        "http://localhost:5173"
    )

    # Cloudinary image storage
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

    # Maximum upload size: 5 MB
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    # Rate-limit storage
    RATELIMIT_STORAGE_URI = os.getenv(
        "RATELIMIT_STORAGE_URI",
        "memory://"
    )
        # Production must use persistent Redis rate-limit storage.
    if APP_ENV == "production" and not RATELIMIT_STORAGE_URI.startswith(
        ("redis://", "rediss://")
    ):
        raise RuntimeError(
            "A Redis URL must be configured for production rate limiting."
        )