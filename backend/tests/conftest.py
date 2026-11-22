import pytest

from app import create_app
from extensions import db, bcrypt
from models import Admin


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-only-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = "Lax"
    RATELIMIT_STORAGE_URI = "memory://"


@pytest.fixture
def app():
    application = create_app(TestConfig)

    with application.app_context():
        db.create_all()

    yield application

    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin(app):
    with app.app_context():
        password_hash = bcrypt.generate_password_hash(
            "TestPassword123!"
        ).decode("utf-8")

        test_admin = Admin(
            username="testadmin",
            email="admin@example.com",
            password_hash=password_hash
        )

        db.session.add(test_admin)
        db.session.commit()

        return test_admin
