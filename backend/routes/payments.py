from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from sqlalchemy.exc import IntegrityError

from flask import Blueprint, request, current_app
from marshmallow import ValidationError

from extensions import db
from models import Payment
from schemas.order_schema import OrderInputSchema
from services.order_service import create_order
from services.payment_service import (
    initiate_stk_push,
    normalize_phone_number,
    MPesaRejectedError,
    MPesaNotSentError,
    query_stk_push,
)
from services.admin_service import update_order_status
from services.email_service import send_order_confirmation
from utils.responses import success_response, error_response


payments_bp = Blueprint(
    "payments",
    __name__,
    url_prefix="/api/payments"
)

order_input_schema = OrderInputSchema()


def send_payment_confirmation(payment):
    """Send and record an order confirmation after verified payment."""

    payment.confirmation_email_status = "sending"
    payment.confirmation_email_attempts += 1
    payment.confirmation_email_last_error = None
    db.session.commit()

    try:
        result = send_order_confirmation(payment.order)
    except Exception:
        current_app.logger.exception(
            "Unexpected confirmation email error for order #%s",
            payment.order_id
        )
        result = False

    if result:
        payment.confirmation_email_status = "sent"
        payment.confirmation_email_sent_at = datetime.now(timezone.utc)
        payment.confirmation_email_last_error = None
    else:
        payment.confirmation_email_status = "failed"
        payment.confirmation_email_last_error = (
            "Resend did not confirm successful email delivery."
        )

        current_app.logger.error(
            "Order confirmation email failed for order #%s",
            payment.order_id
        )

    db.session.commit()
    return result


@payments_bp.route("/stk-push", methods=["POST"])
def start_stk_push():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_response("A valid JSON object is required.")

    try:
        order_data = order_input_schema.load(data)
        phone = normalize_phone_number(
            order_data["customer"]["phone"]
        )

        order = create_order(order_data)
        order_id = order.id

        amount = Decimal(str(order.total_amount))

        if (
            not amount.is_finite()
            or amount <= 0
            or amount != amount.to_integral_value()
        ):
            update_order_status(order, "cancelled")
            return error_response(
                "The order total must be a positive whole-number KSh amount.",
                400
            )

        payment = Payment(
            order_id=order_id,
            phone_number=phone,
            amount=amount,
            status="initiated"
        )

        order.payment_status = "pending"

        db.session.add(payment)
        db.session.commit()

        payment_id = payment.id
        stk_response = None
        ids_saved = False

        try:
            stk_response = initiate_stk_push(
                phone_number=phone,
                amount=amount,
                order_id=order_id
            )

            payment.merchant_request_id = stk_response["merchant_request_id"]
            payment.checkout_request_id = stk_response["checkout_request_id"]
            payment.status = "pending"

            db.session.commit()
            ids_saved = True

        except (MPesaRejectedError, MPesaNotSentError) as error:
            db.session.rollback()

            payment = db.session.get(Payment, payment_id)
            order = db.session.get(type(order), order_id)

            if payment:
                payment.status = "failed"
                payment.result_description = str(error)

            if order:
                order.payment_status = "failed"
                db.session.commit()

                if order.status != "cancelled":
                    update_order_status(order, "cancelled")

            current_app.logger.warning(
                "M-Pesa could not initiate payment for order #%s: %s",
                order_id,
                error
            )

            return error_response(
                "The M-Pesa payment request could not be started. "
                "Your order was cancelled. Please try again.",
                502
            )

        except Exception as error:
            db.session.rollback()

            payment = db.session.get(Payment, payment_id)
            order = db.session.get(type(order), order_id)

            # Safaricom may have accepted the request and returned IDs,
            # even though saving those IDs initially failed.
            ids_saved = False

            if (
                payment
                and isinstance(stk_response, dict)
                and stk_response.get("merchant_request_id")
                and stk_response.get("checkout_request_id")
            ):
                try:
                    payment.merchant_request_id = (
                        stk_response["merchant_request_id"]
                    )
                    payment.checkout_request_id = (
                        stk_response["checkout_request_id"]
                    )
                    payment.status = "pending"
                    payment.result_description = (
                        "Safaricom accepted the STK request. "
                        "Payment verification is pending."
                    )

                    db.session.commit()
                    ids_saved = True

                    current_app.logger.warning(
                        "Recovered STK request IDs for order #%s after a database error.",
                        order_id
                    )

                except Exception:
                    db.session.rollback()

                    current_app.logger.exception(
                        "Could not recover STK request IDs for order #%s.",
                        order_id
                    )

            if not ids_saved:
                payment = db.session.get(Payment, payment_id)
                order = db.session.get(type(order), order_id)

                if payment:
                    payment.status = "unknown"
                    payment.result_description = (
                        "STK Push outcome is uncertain. Reconciliation required."
                    )

                if order:
                    order.payment_status = "pending"

                try:
                    db.session.commit()
                except Exception:
                    db.session.rollback()

                    current_app.logger.exception(
                        "Could not persist uncertain payment status for order #%s.",
                        order_id
                    )

            current_app.logger.exception(
                "Uncertain STK Push result for order #%s",
                order_id
            )

        return success_response(
            data={
                "order_id": order_id,
                "tracking_token": order.tracking_token if order else None,
                "order_status": order.status if order else "pending",
                "payment_status": "pending",
                "payment_result": "pending" if ids_saved else "unknown",
                "amount": str(amount),
                "phone_number": phone,
                "message": (
                    "Your payment request may have reached Safaricom. "
                    "Do not place another order yet. "
                    "Your payment is awaiting verification."
                )
            },
            message="Payment status is being checked.",
            status=202
        )

    except ValidationError as error:
        return error_response(
            "Order validation failed.",
            400,
            error.messages
        )

    except ValueError as error:
        return error_response(str(error), 400)

    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "Unexpected error while starting M-Pesa payment."
        )
        return error_response(
            "Could not start the payment. Please try again.",
            500
        )


def get_callback_metadata(callback):
    """Safely extract values returned in Safaricom callback metadata."""

    if not isinstance(callback, dict):
        return {}

    metadata = callback.get("CallbackMetadata")

    if not isinstance(metadata, dict):
        return {}

    items = metadata.get("Item")

    if not isinstance(items, list):
        return {}

    result = {}

    for item in items:
        if not isinstance(item, dict):
            continue

        name = item.get("Name")

        if isinstance(name, str) and name:
            result[name] = item.get("Value")

    return result


@payments_bp.route("/callback", methods=["POST"])
def mpesa_callback():
    """Verify an STK transaction before updating an order."""

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        current_app.logger.warning("Invalid M-Pesa callback JSON.")
        return success_response(
            data={"accepted": True},
            message="Callback received."
        )

    body = data.get("Body")

    if not isinstance(body, dict):
        current_app.logger.warning("Invalid M-Pesa callback body.")
        return success_response(
            data={"accepted": True},
            message="Callback received."
        )

    callback = body.get("stkCallback")

    if not isinstance(callback, dict):
        current_app.logger.warning("Invalid M-Pesa callback received.")
        return success_response(
            data={"accepted": True},
            message="Callback received."
        )

    checkout_id = callback.get("CheckoutRequestID")
    merchant_id = callback.get("MerchantRequestID")

    if not checkout_id or not merchant_id:
        current_app.logger.warning(
            "M-Pesa callback missing transaction identifiers."
        )
        return success_response(
            data={"accepted": True},
            message="Callback received."
        )

    payment = Payment.query.filter_by(
        checkout_request_id=checkout_id
    ).with_for_update().first()

    if not payment or payment.merchant_request_id != merchant_id:
        current_app.logger.warning(
            "Unmatched M-Pesa callback received."
        )
        return success_response(
            data={"accepted": True},
            message="Callback received."
        )

    # A paid payment may still need its confirmation email retried.
    if payment.status == "paid":
        if payment.confirmation_email_status in {"pending", "failed"}:
            send_payment_confirmation(payment)

        return success_response(
            data={
                "accepted": True,
                "payment_status": "paid",
                "confirmation_email_status": payment.confirmation_email_status
            },
            message="Payment already verified."
        )

    if payment.status == "failed":
        return success_response(
            data={"accepted": True, "payment_status": "failed"},
            message="Callback already processed."
        )

    try:
        callback_result = int(callback.get("ResultCode"))
    except (TypeError, ValueError):
        callback_result = None

    metadata = get_callback_metadata(callback)

    try:
        # Always ask Safaricom for the actual transaction result.
        query_result = query_stk_push(checkout_id)

        if not isinstance(query_result, dict):
            raise RuntimeError("Invalid Safaricom query response.")

        if str(query_result.get("ResponseCode")) != "0":
            raise RuntimeError("Safaricom did not accept the transaction query.")

        if query_result.get("CheckoutRequestID") != checkout_id:
            raise RuntimeError("Safaricom returned a mismatched transaction.")

        if query_result.get("MerchantRequestID") != merchant_id:
            raise RuntimeError("Safaricom returned a mismatched merchant request.")

        query_code = query_result.get("ResultCode")

        if query_code is None:
            raise RuntimeError("Safaricom has not confirmed the transaction result.")

        query_code = int(query_code)

    except Exception:
        current_app.logger.exception(
            "Could not verify M-Pesa payment for order #%s",
            payment.order_id
        )

        payment.status = "unknown"
        payment.result_description = (
            "Safaricom verification is pending. Do not treat this payment as paid."
        )
        db.session.commit()

        return success_response(
            data={"accepted": True, "payment_status": "pending"},
            message="Payment verification is pending."
        )

    order = payment.order

    if query_code != 0:
        payment.status = "failed"
        payment.result_code = query_code
        payment.result_description = query_result.get(
            "ResultDesc",
            "Safaricom confirmed that the payment failed."
        )

        order.payment_status = "failed"
        db.session.commit()

        if order.status != "cancelled":
            update_order_status(order, "cancelled")

        current_app.logger.info(
            "M-Pesa payment failed for order #%s",
            order.id
        )

        return success_response(
            data={"accepted": True, "payment_status": "failed"},
            message="Payment failure recorded."
        )

    # A successful query must agree with the callback.
    try:
        callback_amount = Decimal(str(metadata["Amount"]))
        callback_phone = normalize_phone_number(
            str(metadata["PhoneNumber"])
        )
        raw_receipt = metadata["MpesaReceiptNumber"]

        if not isinstance(raw_receipt, str):
            raise ValueError("Invalid M-Pesa receipt number.")

        receipt = raw_receipt.strip()

        if not receipt or receipt.lower() == "none":
            raise ValueError("Missing M-Pesa receipt number.")
        if (
            callback_result != 0
            or callback_amount != payment.amount
            or callback_phone != payment.phone_number
            or not receipt
        ):
            raise ValueError("Payment details do not match the stored order.")

    except (KeyError, TypeError, ValueError, InvalidOperation):
        payment.status = "unknown"
        payment.result_description = (
            "Safaricom transaction result received, but callback details "
            "could not be verified."
        )
        db.session.commit()

        current_app.logger.warning(
            "M-Pesa verification details did not match order #%s",
            order.id
        )

        return success_response(
            data={"accepted": True, "payment_status": "pending"},
            message="Payment requires further verification."
        )

    payment.status = "paid"
    payment.result_code = 0
    payment.result_description = query_result.get(
        "ResultDesc",
        "Payment completed successfully."
    )
    payment.mpesa_receipt_number = receipt

    order.payment_status = "paid"

    payment_id = payment.id
    order_id = order.id

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

        payment = db.session.get(Payment, payment_id)

        if payment:
            payment.status = "unknown"
            payment.result_description = (
                "Receipt number is already associated with another payment. "
                "Manual verification is required."
            )
            payment.order.payment_status = "pending"
            db.session.commit()

        current_app.logger.exception(
            "M-Pesa receipt conflict for order #%s",
            order_id
        )

        return success_response(
            data={"accepted": True, "payment_status": "pending"},
            message="Payment requires further verification."
        )

    # Send confirmation only after verified payment.
    send_payment_confirmation(payment)

    current_app.logger.info(
        "M-Pesa payment verified for order #%s. Receipt: %s",
        order.id,
        receipt
    )

    return success_response(
        data={
            "accepted": True,
            "order_id": order.id,
            "payment_status": "paid",
            "receipt_number": receipt
        },
        message="Payment verified successfully."
    )
