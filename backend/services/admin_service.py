from sqlalchemy import func

from extensions import db
from models import Order, Product


ALLOWED_ORDER_STATUSES = {
    "pending",
    "confirmed",
    "processing",
    "shipped",
    "delivered",
    "cancelled"
}


def get_dashboard_stats():
    total_orders = Order.query.count()

    pending_orders = Order.query.filter_by(
        status="pending"
    ).count()

    completed_orders = Order.query.filter_by(
        status="delivered"
    ).count()

    cancelled_orders = Order.query.filter_by(
        status="cancelled"
    ).count()

    order_value = db.session.query(
        func.coalesce(func.sum(Order.total_amount), 0)
    ).filter(
        Order.status != "cancelled"
    ).scalar()

    return {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "completed_orders": completed_orders,
        "cancelled_orders": cancelled_orders,
        "total_order_value": str(order_value)
    }


def get_all_orders(status=None):
    query = Order.query

    if status:
        query = query.filter_by(status=status)

    return query.order_by(Order.created_at.desc()).all()


def get_order_by_id(order_id):
    return db.session.get(Order, order_id)


def update_order_status(order, new_status):
    if new_status not in ALLOWED_ORDER_STATUSES:
        raise ValueError(
            "Invalid order status. Allowed statuses: "
            + ", ".join(sorted(ALLOWED_ORDER_STATUSES))
        )

    try:
        # Lock the order while changing its status.
        locked_order = (
            Order.query
            .filter_by(id=order.id)
            .with_for_update()
            .first()
        )

        if locked_order is None:
            raise ValueError("Order not found.")

        previous_status = locked_order.status

        # Do not process the same status transition twice.
        if previous_status == new_status:
            return locked_order

        # Cancelled orders cannot be reopened.
        if previous_status == "cancelled":
            raise ValueError(
                "Cancelled orders cannot be reopened."
            )

        # Do not cancel orders while M-Pesa payment is pending
        # or its result is still being verified.
        if (
            new_status == "cancelled"
            and locked_order.payment_status == "pending"
        ):
            raise ValueError(
                "Orders with pending or unverified payments cannot be cancelled."
            )

        # Do not cancel paid orders until a refund process exists.
        if (
            new_status == "cancelled"
            and locked_order.payment_status == "paid"
        ):
            raise ValueError(
                "Paid orders cannot be cancelled before a refund is processed."
            )

        # Do not return stock for orders already shipped or delivered.
        if new_status == "cancelled" and previous_status in {
            "shipped",
            "delivered"
        }:
            raise ValueError(
                "Shipped or delivered orders cannot be cancelled."
            )

        # Restore stock when an order is cancelled.
        if new_status == "cancelled":
            for item in locked_order.items:

                product = (
                    Product.query
                    .filter_by(id=item.product_id)
                    .with_for_update()
                    .first()
                )

                if product is None:
                    raise ValueError(
                        f"Product {item.product_id} not found."
                    )

                product.stock += item.quantity

        locked_order.status = new_status

        # Save the stock restoration and status change together.
        db.session.commit()

        return locked_order

    except Exception:
        db.session.rollback()
        raise
