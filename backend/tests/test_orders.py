from decimal import Decimal

import pytest

from extensions import db
from models import Product, Order, OrderItem, Customer
from services.order_service import create_order
from services.admin_service import update_order_status


def create_test_product(
    name="Test Sticker",
    price=Decimal("100.00"),
    stock=10,
    is_active=True
):
    product = Product(
        name=name,
        price=price,
        stock=stock,
        is_active=is_active
    )

    db.session.add(product)
    db.session.flush()

    product_id = product.id

    db.session.commit()

    return product_id


def make_order_data(product_id, quantity=1):
    return {
        "customer": {
            "name": "Test Customer",
            "email": "customer@example.com",
            "phone": "0712345678",
            "address": "Nairobi, Kenya"
        },
        "items": [
            {
                "product_id": product_id,
                "quantity": quantity
            }
        ]
    }


def test_order_uses_database_price_not_submitted_price(app):
    with app.app_context():
        product_id = create_test_product(
            price=Decimal("100.00"),
            stock=5
        )

        order_data = make_order_data(product_id)
        order_data["items"][0]["price"] = "0.01"

        order = create_order(order_data)

        assert order.total_amount == Decimal("100.00")
        assert order.items[0].unit_price == Decimal("100.00")


def test_order_reduces_stock(app):
    with app.app_context():
        product_id = create_test_product(stock=5)

        create_order(make_order_data(product_id, quantity=2))

        product = db.session.get(Product, product_id)

        assert product.stock == 3


def test_duplicate_product_ids_are_combined(app):
    with app.app_context():
        product_id = create_test_product(stock=10)

        order_data = make_order_data(product_id, quantity=2)
        order_data["items"].append({
            "product_id": product_id,
            "quantity": 3
        })

        order = create_order(order_data)

        product = db.session.get(Product, product_id)

        assert len(order.items) == 1
        assert order.items[0].quantity == 5
        assert product.stock == 5


def test_order_rejects_insufficient_stock(app):
    with app.app_context():
        product_id = create_test_product(stock=2)

        with pytest.raises(ValueError, match="Insufficient stock"):
            create_order(make_order_data(product_id, quantity=3))

        product = db.session.get(Product, product_id)

        assert product.stock == 2
        assert Order.query.count() == 0
        assert Customer.query.count() == 0


def test_order_rejects_inactive_product(app):
    with app.app_context():
        product_id = create_test_product(
            stock=5,
            is_active=False
        )

        with pytest.raises(ValueError, match="unavailable"):
            create_order(make_order_data(product_id))

        product = db.session.get(Product, product_id)

        assert product.stock == 5
        assert Order.query.count() == 0


def test_order_rejects_nonexistent_product(app):
    with app.app_context():
        with pytest.raises(ValueError, match="unavailable"):
            create_order(make_order_data(99999))

        assert Order.query.count() == 0

def test_cancelling_order_restores_stock(app):
    with app.app_context():
        product_id = create_test_product(stock=10)

        order = create_order(
            make_order_data(product_id, quantity=3)
        )

        product = db.session.get(Product, product_id)
        assert product.stock == 7

        update_order_status(order, "cancelled")

        product = db.session.get(Product, product_id)
        order = db.session.get(Order, order.id)

        assert product.stock == 10
        assert order.status == "cancelled"


def test_cancelling_order_twice_does_not_restore_stock_twice(app):
    with app.app_context():
        product_id = create_test_product(stock=10)

        order = create_order(
            make_order_data(product_id, quantity=3)
        )

        update_order_status(order, "cancelled")
        update_order_status(order, "cancelled")

        product = db.session.get(Product, product_id)

        assert product.stock == 10


def test_cancelling_shipped_order_is_rejected(app):
    with app.app_context():
        product_id = create_test_product(stock=10)

        order = create_order(
            make_order_data(product_id, quantity=3)
        )

        update_order_status(order, "shipped")

        with pytest.raises(ValueError, match="cannot be cancelled"):
            update_order_status(order, "cancelled")

        product = db.session.get(Product, product_id)

        assert product.stock == 7


def test_cancelled_order_cannot_be_reopened(app):
    with app.app_context():
        product_id = create_test_product(stock=10)

        order = create_order(
            make_order_data(product_id, quantity=3)
        )

        update_order_status(order, "cancelled")

        with pytest.raises(ValueError, match="cannot be reopened"):
            update_order_status(order, "confirmed")

        product = db.session.get(Product, product_id)

        assert product.stock == 10
