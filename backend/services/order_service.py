import secrets
from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Customer, Product, Order, OrderItem


def create_order(order_data):
    """
    Create a customer order.

    - Reuse an existing customer when the email already exists.
    - Validate products and stock.
    - Calculate prices using database values.
    - Save order and order items.
    - Reduce product stock.
    - Roll back everything if an error occurs.
    """

    customer_data = order_data["customer"]
    requested_items = order_data["items"]

    # Combine duplicate product IDs into one quantity.
    quantities = {}

    for item in requested_items:
        product_id = item["product_id"]
        quantity = item["quantity"]

        quantities[product_id] = (
            quantities.get(product_id, 0) + quantity
        )

    try:
        with db.session.begin():

            # Find the customer using their email.
            customer = Customer.query.filter_by(
                email=customer_data["email"]
            ).first()

            if customer is None:
                customer = Customer(**customer_data)
                db.session.add(customer)
                db.session.flush()
            else:
                # Keep the customer's contact information updated.
                customer.name = customer_data["name"]
                customer.phone = customer_data["phone"]
                customer.address = customer_data["address"]

            # Retrieve all requested products.
            products = Product.query.filter(
                Product.id.in_(quantities.keys())
            ).all()

            product_map = {
                product.id: product for product in products
            }

            # Check that every requested product exists and is active.
            for product_id, quantity in quantities.items():

                product = product_map.get(product_id)

                if product is None or not product.is_active:
                    raise ValueError(
                        f"Product {product_id} is unavailable."
                    )

                if product.stock < quantity:
                    raise ValueError(
                        f"Insufficient stock for {product.name}. "
                        f"Available: {product.stock}, requested: {quantity}."
                    )

            # Calculate the total using database prices.
            total_amount = Decimal("0.00")

            for product_id, quantity in quantities.items():
                product = product_map[product_id]
                total_amount += product.price * quantity

            # Create the order.
            order = Order(
                customer_id=customer.id,
                total_amount=total_amount,
                status="pending",
                tracking_token=secrets.token_hex(32)
            )

            db.session.add(order)
            db.session.flush()

            # Create order items and reduce stock.
            for product_id, quantity in quantities.items():

                product = product_map[product_id]

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=product.price
                )

                db.session.add(order_item)

                product.stock -= quantity

            db.session.flush()

        return order

    except IntegrityError as error:
        db.session.rollback()
        raise ValueError(
            "Could not create the order. Please try again."
        ) from error
