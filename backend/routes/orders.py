
from flask import Blueprint, request
from marshmallow import ValidationError

from extensions import db
from models import Order
from schemas.order_schema import OrderInputSchema
from schemas.customer_schema import CustomerSchema
from services.order_service import create_order
from utils.responses import success_response, error_response
from utils.decorators import admin_required

orders_bp = Blueprint(
    "orders",
    __name__,
    url_prefix="/api/orders"
)

order_input_schema = OrderInputSchema()
customer_schema = CustomerSchema()


def serialize_order(order):
    """Convert an order and its relationships into JSON-friendly data."""

    return {
        "id": order.id,
        "total_amount": str(order.total_amount),
        "status": order.status,
        "payment_status": order.payment_status,
        "created_at": (
            order.created_at.isoformat()
            if order.created_at else None
        ),
        "customer": customer_schema.dump(order.customer),
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "unit_price": str(item.unit_price),
                "subtotal": str(item.unit_price * item.quantity)
            }
            for item in order.items
        ]
    }


@orders_bp.route("", methods=["POST"])
def place_order():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_response("A valid JSON object is required")

    try:
        order_data = order_input_schema.load(data)
	
        order = create_order(order_data)

        order_data = serialize_order(order)

        order_data["tracking_token"] = order.tracking_token

        order_data = {
            "id": order.id,
            "status": order.status,
            "payment_status": order.payment_status,
            "total_amount": str(order.total_amount),
            "created_at": (
                order.created_at.isoformat()
                if order.created_at else None
            ),
            "tracking_token": order.tracking_token,
            "items": [
                {
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "unit_price": str(item.unit_price),
                    "subtotal": str(
                        item.unit_price * item.quantity
                    )
                }
                for item in order.items
            ]
        }

        return success_response(
            data=order_data,
            message="Order created successfully",
            status=201
        )

    except ValidationError as error:
        return error_response(
            "Order validation failed",
            400,
            error.messages
        )

    except ValueError as error:
        return error_response(str(error), 400)


@orders_bp.route("/<int:order_id>", methods=["GET"])
@admin_required
def retrieve_order(order_id):

    order = db.session.get(Order, order_id)

    if order is None:
        return error_response("Order not found", 404)

    return success_response(
        data=serialize_order(order),
        message="Order retrieved successfully"
    )
@orders_bp.route("/track/<string:tracking_token>", methods=["GET"])
def track_order(tracking_token):
    order = Order.query.filter_by(
        tracking_token=tracking_token
    ).first()

    if order is None:
        return error_response("Order not found", 404)

    order_data = {
        "id": order.id,
        "status": order.status,
        "payment_status": order.payment_status,
        "total_amount": str(order.total_amount),
        "created_at": (
            order.created_at.isoformat()
            if order.created_at else None
        ),
        "items": [
            {
                "product_name": item.product.name,
                "quantity": item.quantity,
                "unit_price": str(item.unit_price),
                "subtotal": str(
                    item.unit_price * item.quantity
                )
            }
            for item in order.items
        ]
    }

    return success_response(
        data=order_data,
        message="Order retrieved successfully"
    )
