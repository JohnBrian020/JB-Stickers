import logging
from html import escape

import resend
from flask import current_app

logger = logging.getLogger(__name__)


def send_email(to_email, subject, html_content, text_content=None):
    """Send an email through Resend."""

    api_key = current_app.config.get("RESEND_API_KEY")
    sender = current_app.config.get("MAIL_FROM")

    if not api_key or not sender:
        logger.warning(
            "Email not sent: Resend configuration is missing."
        )
        return False

    try:
        resend.api_key = api_key

        email_data = {
            "from": sender,
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        }

        if text_content:
            email_data["text"] = text_content

        response = resend.Emails.send(email_data)

        logger.info("Email accepted by Resend for %s", to_email)
        return response

    except Exception:
        logger.exception("Failed to send email to %s", to_email)
        return False


def send_order_confirmation(order):
    """Send an order confirmation with a private tracking link."""

    customer = order.customer

    frontend_url = current_app.config.get(
        "FRONTEND_URL",
        "http://localhost:5173"
    ).rstrip("/")

    tracking_url = (
        f"{frontend_url}/order-confirmation/{order.tracking_token}"
    )

    item_rows = ""
    text_items = []

    for item in order.items:
        product_name = escape(item.product.name)
        quantity = item.quantity
        subtotal = item.unit_price * quantity

        item_rows += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">
                    {product_name}
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">
                    {quantity}
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">
                    KSh {subtotal:,.2f}
                </td>
            </tr>
        """

        text_items.append(
            f"{item.product.name} x {quantity} - KSh {subtotal:,.2f}"
        )

    customer_name = escape(customer.name)
    total = f"KSh {order.total_amount:,.2f}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: auto; padding: 24px;">
            <h1 style="color: #e85d75;">XOXO Stickers</h1>

            <h2>Thank you for your order, {customer_name}!</h2>

            <p>Your order has been received successfully.</p>

            <p><strong>Order number:</strong> #{order.id}</p>
            <p><strong>Status:</strong> {escape(order.status.title())}</p>

            <h3>Order summary</h3>

            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr>
                        <th align="left">Product</th>
                        <th align="left">Quantity</th>
                        <th align="left">Subtotal</th>
                    </tr>
                </thead>
                <tbody>
                    {item_rows}
                </tbody>
            </table>

            <h3>Total: {total}</h3>

            <p>
                <a href="{escape(tracking_url, quote=True)}"
                   style="display: inline-block; padding: 12px 20px;
                   background: #e85d75; color: white;
                   text-decoration: none; border-radius: 5px;">
                    Track your order
                </a>
            </p>

            <p>Thank you for shopping with XOXO Stickers!</p>
        </div>
    </body>
    </html>
    """

    text_content = f"""
Hello {customer.name},

Thank you for your order!

Order number: #{order.id}
Status: {order.status.title()}

Items:
{chr(10).join(text_items)}

Total: {total}

Track your order:
{tracking_url}

Thank you for shopping with XOXO Stickers!
"""

    return send_email(
        customer.email,
        f"Order Confirmation - #{order.id}",
        html_content,
        text_content
    )
def send_order_status_update(order, new_status):
    """Notify a customer when their order status changes."""

    customer = order.customer

    frontend_url = current_app.config.get(
        "FRONTEND_URL",
        "http://localhost:5173"
    ).rstrip("/")

    tracking_url = (
        f"{frontend_url}/order-confirmation/{order.tracking_token}"
    )

    status_messages = {
        "confirmed": (
            "Your order has been confirmed!",
            "We've accepted your order and will prepare it shortly."
        ),
        "shipped": (
            "Your order is on its way!",
            "Your order has been dispatched."
        ),
        "delivered": (
            "Your order has been delivered!",
            "We hope you enjoy your stickers."
        ),
        "cancelled": (
            "Your order has been cancelled.",
            "Please contact us if you have questions about this cancellation."
        )
    }

    if new_status not in status_messages:
        return False

    heading, message = status_messages[new_status]

    customer_name = escape(customer.name)
    safe_tracking_url = escape(tracking_url, quote=True)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: auto; padding: 24px;">
            <h1 style="color: #e85d75;">XOXO Stickers</h1>

            <h2>Hello {customer_name}!</h2>

            <h3>{heading}</h3>

            <p>{message}</p>

            <p><strong>Order number:</strong> #{order.id}</p>

            <p>
                <strong>Current status:</strong>
                {escape(new_status.title())}
            </p>

            <p>
                <a href="{safe_tracking_url}"
                   style="display: inline-block; padding: 12px 20px;
                   background: #e85d75; color: white;
                   text-decoration: none; border-radius: 5px;">
                    Track your order
                </a>
            </p>

            <p>Thank you for shopping with XOXO Stickers!</p>
        </div>
    </body>
    </html>
    """

    text_content = f"""
Hello {customer.name},

{heading}

{message}

Order number: #{order.id}
Current status: {new_status.title()}

Track your order:
{tracking_url}

Thank you for shopping with XOXO Stickers!
"""

    return send_email(
        customer.email,
        f"Order Update - #{order.id}: {new_status.title()}",
        html_content,
        text_content
    )
