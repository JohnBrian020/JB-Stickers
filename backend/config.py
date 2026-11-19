import os
from datetime import timedelta


class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "development-secret-key-change-later"
    )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///jb_stickers.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True

    SESSION_COOKIE_SAMESITE = os.getenv(
        "SESSION_COOKIE_SAMESITE",
        "Lax"
    )

    SESSION_COOKIE_SECURE = (
        os.getenv("SESSION_COOKIE_SECURE", "false").lower()
        == "true"
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
