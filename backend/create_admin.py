
import os
from getpass import getpass

from app import app
from extensions import db, bcrypt
from models import Admin


def create_admin():
    print("\nJB Stickers - Create Administrator\n")

    username = os.getenv("ADMIN_USERNAME")
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")

    # Interactive fallback for local use.
    if not all([username, email, password]):
        username = input("Admin username: ").strip()
        email = input("Admin email: ").strip().lower()
        password = getpass("Admin password: ")
        confirm_password = getpass("Confirm password: ")

        if password != confirm_password:
            print("Passwords do not match.")
            return

    username = username.strip()
    email = email.strip().lower()

    if not username or not email:
        print("Username and email are required.")
        return

    if len(password) < 12:
        print("Password must contain at least 12 characters.")
        return

    with app.app_context():
        existing_admin = Admin.query.filter(
            (Admin.username == username) |
            (Admin.email == email)
        ).first()

        if existing_admin:
            print("An administrator with that username or email already exists.")
            return

        password_hash = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        admin = Admin(
            username=username,
            email=email,
            password_hash=password_hash
        )

        db.session.add(admin)
        db.session.commit()

        print("\nAdministrator created successfully!")
        print(f"Username: {admin.username}")
        print(f"Email: {admin.email}")


if __name__ == "__main__":
    create_admin()
