import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import db, migrate, bcrypt
from models import Product, Customer, Order, OrderItem, Admin
from routes.products import products_bp
from routes.orders import orders_bp
from routes.auth import auth_bp
from routes.admin import admin_bp


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)

    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    allowed_origins = os.getenv(
        "FRONTEND_URL",
        "http://localhost:5173"
    ).split(",")

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": allowed_origins
            }
        },
        supports_credentials=True
    )

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "success",
            "message": "JB Stickers API is running"
        }), 200

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
