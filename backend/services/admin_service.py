
from sqlalchemy import func

from extensions import db
from models import Order


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

    # Exclude cancelled orders from the order value.
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

    order.status = new_status
    db.session.commit()

    return order
