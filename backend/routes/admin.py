
from flask import Blueprint, request

from schemas.customer_schema import CustomerSchema
from services.email_service import send_order_status_update
from services.admin_service import (
    get_dashboard_stats,
    get_all_orders,
    get_order_by_id,
    update_order_status
)
from utils.decorators import admin_required
from utils.responses import success_response, error_response


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/api/admin"
)

customer_schema = CustomerSchema()


def serialize_order(order, include_payments=False):
    data = {
        "id": order.id,
        "total_amount": str(order.total_amount),
        "status": order.status,
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
                "subtotal": str(
                    item.unit_price * item.quantity
                )
            }
            for item in order.items
        ]
    }

    if include_payments:
        data["payment_status"] = order.payment_status
        data["payments"] = [
            {
                "id": payment.id,
                "method": "M-Pesa",
                "phone_number": payment.phone_number,
                "amount": str(payment.amount),
                "status": payment.status,
                "mpesa_receipt_number": payment.mpesa_receipt_number,
                "created_at": (
                    payment.created_at.isoformat()
                    if payment.created_at else None
                ),
                "updated_at": (
                    payment.updated_at.isoformat()
                    if payment.updated_at else None
                )
            }
            for payment in order.payments
        ]

    return data


@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def dashboard():
    stats = get_dashboard_stats()

    return success_response(
        data=stats,
        message="Dashboard statistics retrieved successfully"
    )


@admin_bp.route("/orders", methods=["GET"])
@admin_required
def list_orders():
    status = request.args.get("status")

    orders = get_all_orders(status=status)

    orders_data = [
        serialize_order(order)
        for order in orders
    ]

    return success_response(
        data=orders_data,
        message="Orders retrieved successfully"
    )


@admin_bp.route("/orders/<int:order_id>", methods=["GET"])
@admin_required
def order_details(order_id):
    order = get_order_by_id(order_id)

    if order is None:
        return error_response("Order not found", 404)

    return success_response(
        data=serialize_order(order, include_payments=True),
        message="Order retrieved successfully"
    )


@admin_bp.route(
    "/orders/<int:order_id>/status",
    methods=["PATCH"]
)
@admin_required
def change_order_status(order_id):
    order = get_order_by_id(order_id)

    if order is None:
        return error_response("Order not found", 404)

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_response("A valid JSON object is required")

    new_status = data.get("status")

    if not isinstance(new_status, str) or not new_status.strip():
        return error_response("Order status is required")

    try:
        new_status = new_status.strip().lower()
        previous_status = order.status

        order = update_order_status(order, new_status)

        if (
            previous_status != order.status
            and order.status in {
                "confirmed",
                "shipped",
                "delivered",
                "cancelled"
            }
        ):
            send_order_status_update(order, order.status)

        return success_response(
            data=serialize_order(order, include_payments=True),
            message="Order status updated successfully"
        )

    except ValueError as error:
        return error_response(str(error), 400)
