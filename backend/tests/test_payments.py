from decimal import Decimal

import pytest

from extensions import db
from models import Product, Payment, Order
from services.order_service import create_order
from services.payment_service import MPesaNotSentError, MPesaUncertainError
from sqlalchemy.orm import Session


def create_payment_order():
    product = Product(
        name="Payment Test Sticker",
        price=Decimal("100.00"),
        stock=10,
        is_active=True
    )
    db.session.add(product)
    db.session.commit()
    product_id = product.id
    db.session.remove()

    order = create_order({
        "customer": {
            "name": "Payment Customer",
            "email": "payment@example.com",
            "phone": "0712345678",
            "address": "Nairobi, Kenya"
        },
        "items": [
            {
                "product_id": product_id,
                "quantity": 2
            }
        ]
    })

    payment = Payment(
        order_id=order.id,
        phone_number="254712345678",
        amount=Decimal("200.00"),
        merchant_request_id="merchant-123",
        checkout_request_id="checkout-123",
        status="pending"
    )

    order.payment_status = "pending"
    db.session.add(payment)
    db.session.commit()

    return order.id, payment.id, product.id


def successful_query():
    return {
        "ResponseCode": "0",
        "MerchantRequestID": "merchant-123",
        "CheckoutRequestID": "checkout-123",
        "ResultCode": "0",
        "ResultDesc": "The service request is processed successfully."
    }


def successful_callback():
    return {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "merchant-123",
                "CheckoutRequestID": "checkout-123",
                "ResultCode": 0,
                "ResultDesc": "The service request is processed successfully.",
                "CallbackMetadata": {
                    "Item": [
                        {"Name": "Amount", "Value": 200},
                        {"Name": "MpesaReceiptNumber", "Value": "TEST123456"},
                        {"Name": "PhoneNumber", "Value": 254712345678}
                    ]
                }
            }
        }
    }


def test_successful_callback_marks_payment_paid(
    app, client, monkeypatch
):
    with app.app_context():
        order_id, payment_id, product_id = create_payment_order()

    email_calls = []

    monkeypatch.setattr(
        "routes.payments.query_stk_push",
        lambda checkout_id: successful_query()
    )
    monkeypatch.setattr(
        "routes.payments.send_order_confirmation",
        lambda order: (email_calls.append(order.id), True)[1]
    )

    response = client.post(
        "/api/payments/callback",
        json=successful_callback()
    )

    assert response.status_code == 200

    with app.app_context():
        payment = db.session.get(Payment, payment_id)
        order = db.session.get(Order, order_id)

        assert payment.status == "paid"
        assert payment.mpesa_receipt_number == "TEST123456"
        assert order.payment_status == "paid"

    assert email_calls == [order_id]


def test_failed_callback_cancels_order_and_restores_stock(
    app, client, monkeypatch
):
    with app.app_context():
        order_id, payment_id, product_id = create_payment_order()

    monkeypatch.setattr(
        "routes.payments.query_stk_push",
        lambda checkout_id: {
            **successful_query(),
            "ResultCode": "1",
            "ResultDesc": "The transaction was cancelled."
        }
    )

    response = client.post(
        "/api/payments/callback",
        json=successful_callback()
    )

    assert response.status_code == 200

    with app.app_context():
        payment = db.session.get(Payment, payment_id)
        order = db.session.get(Order, order_id)
        product = db.session.get(Product, product_id)

        assert payment.status == "failed"
        assert order.payment_status == "failed"
        assert order.status == "cancelled"
        assert product.stock == 10


def test_amount_mismatch_does_not_mark_payment_paid(
    app, client, monkeypatch
):
    with app.app_context():
        order_id, payment_id, product_id = create_payment_order()

    monkeypatch.setattr(
        "routes.payments.query_stk_push",
        lambda checkout_id: successful_query()
    )
    monkeypatch.setattr(
        "routes.payments.send_order_confirmation",
        lambda order: pytest.fail("Email must not be sent.")
    )

    callback = successful_callback()
    callback["Body"]["stkCallback"]["CallbackMetadata"]["Item"][0]["Value"] = 50

    response = client.post(
        "/api/payments/callback",
        json=callback
    )

    assert response.status_code == 200

    with app.app_context():
        payment = db.session.get(Payment, payment_id)
        order = db.session.get(Order, order_id)

        assert payment.status == "unknown"
        assert order.payment_status == "pending"


def test_query_error_keeps_payment_pending(
    app, client, monkeypatch
):
    with app.app_context():
        order_id, payment_id, product_id = create_payment_order()

    def failed_query(checkout_id):
        raise RuntimeError("Safaricom unavailable")

    monkeypatch.setattr(
        "routes.payments.query_stk_push",
        failed_query
    )

    response = client.post(
        "/api/payments/callback",
        json=successful_callback()
    )

    assert response.status_code == 200

    with app.app_context():
        payment = db.session.get(Payment, payment_id)
        order = db.session.get(Order, order_id)

        assert payment.status == "unknown"
        assert order.payment_status == "pending"


def test_malformed_callback_json_is_safely_acknowledged(client):
    response = client.post(
        "/api/payments/callback",
        json=[]
    )

    assert response.status_code == 200


def test_rejected_safaricom_query_keeps_payment_pending(
    app, client, monkeypatch
):
    with app.app_context():
        order_id, payment_id, product_id = create_payment_order()

    monkeypatch.setattr(
        "routes.payments.query_stk_push",
        lambda checkout_id: {
            **successful_query(),
            "ResponseCode": "1",
            "ResultCode": "1"
        }
    )

    response = client.post(
        "/api/payments/callback",
        json=successful_callback()
    )

    assert response.status_code == 200

    with app.app_context():
        payment = db.session.get(Payment, payment_id)
        order = db.session.get(Order, order_id)
        product = db.session.get(Product, product_id)

        assert payment.status == "unknown"
        assert order.payment_status == "pending"
        assert order.status != "cancelled"
        assert product.stock == 8



def create_stk_request_data():
    product = Product(
        name="STK Test Sticker",
        price=Decimal("100.00"),
        stock=10,
        is_active=True
    )
    db.session.add(product)
    db.session.commit()

    return product.id, {
        "customer": {
            "name": "STK Test Customer",
            "email": "stk@example.com",
            "phone": "0712345678",
            "address": "Nairobi, Kenya"
        },
        "items": [
            {
                "product_id": product.id,
                "quantity": 2
            }
        ]
    }


def test_stk_auth_failure_cancels_order_and_restores_stock(
    app, client, monkeypatch
):
    with app.app_context():
        product_id, order_data = create_stk_request_data()

    def fail_before_sending(**kwargs):
        raise MPesaNotSentError("OAuth authentication failed.")

    monkeypatch.setattr(
        "routes.payments.initiate_stk_push",
        fail_before_sending
    )

    response = post_with_csrf(
        client,
        "/api/payments/stk-push",
        order_data
    )

    assert response.status_code == 502

    with app.app_context():
        order = Order.query.order_by(Order.id.desc()).first()
        payment = Payment.query.filter_by(order_id=order.id).first()
        product = db.session.get(Product, product_id)

        assert payment.status == "failed"
        assert order.payment_status == "failed"
        assert order.status == "cancelled"
        assert product.stock == 10


def test_stk_timeout_keeps_order_pending_and_stock_reserved(
    app, client, monkeypatch
):
    with app.app_context():
        product_id, order_data = create_stk_request_data()

    def simulate_timeout(**kwargs):
        raise MPesaUncertainError("Safaricom response timed out.")

    monkeypatch.setattr(
        "routes.payments.initiate_stk_push",
        simulate_timeout
    )

    response = post_with_csrf(
        client,
        "/api/payments/stk-push",
        order_data
    )

    assert response.status_code == 202

    with app.app_context():
        order = Order.query.order_by(Order.id.desc()).first()
        payment = Payment.query.filter_by(order_id=order.id).first()
        product = db.session.get(Product, product_id)

        assert payment.status == "unknown"
        assert order.payment_status == "pending"
        assert order.status != "cancelled"
        assert product.stock == 8
def test_stk_request_ids_are_recovered_after_database_commit_failure(
    app, client, monkeypatch
):
    with app.app_context():
        product_id, order_data = create_stk_request_data()

    state = {
        "stk_response_received": False,
        "commit_failed": False
    }

    def successful_stk_push(**kwargs):
        state["stk_response_received"] = True

        return {
            "merchant_request_id": "merchant-recovered",
            "checkout_request_id": "checkout-recovered",
            "customer_message": "STK Push sent successfully."
        }

    original_commit = Session.commit

    def fail_first_commit_after_stk(self):
        if (
            state["stk_response_received"]
            and not state["commit_failed"]
        ):
            state["commit_failed"] = True
            raise RuntimeError("Simulated database commit failure.")

        return original_commit(self)

    monkeypatch.setattr(
        "routes.payments.initiate_stk_push",
        successful_stk_push
    )

    monkeypatch.setattr(
        Session,
        "commit",
        fail_first_commit_after_stk
    )

    response = post_with_csrf(
        client,
        "/api/payments/stk-push",
        order_data
    )

    assert response.status_code == 202
    assert state["commit_failed"] is True

    with app.app_context():
        order = Order.query.order_by(Order.id.desc()).first()
        payment = Payment.query.filter_by(order_id=order.id).first()
        product = db.session.get(Product, product_id)

        assert payment.merchant_request_id == "merchant-recovered"
        assert payment.checkout_request_id == "checkout-recovered"
        assert payment.status == "pending"

        assert order.payment_status == "pending"
        assert order.status != "cancelled"
        assert product.stock == 8

def post_with_csrf(client, url, json):
    token = "test-csrf-token"

    with client.session_transaction() as session:
        session["csrf_token"] = token

    return client.post(
        url,
        json=json,
        headers={"X-CSRFToken": token}
    )


@pytest.mark.parametrize(
    "metadata",
    [
        None,
        "invalid",
        [],
        {"Item": "invalid"},
        {"Item": [None, "invalid", {"Name": "Amount"}]},
    ],
)
def test_malformed_callback_metadata_keeps_payment_pending(
    app, client, monkeypatch, metadata
):
    with app.app_context():
        order_id, payment_id, product_id = create_payment_order()

    monkeypatch.setattr(
        "routes.payments.query_stk_push",
        lambda checkout_id: successful_query()
    )

    callback = successful_callback()
    callback["Body"]["stkCallback"]["CallbackMetadata"] = metadata

    response = client.post(
        "/api/payments/callback",
        json=callback
    )

    assert response.status_code == 200

    with app.app_context():
        payment = db.session.get(Payment, payment_id)
        order = db.session.get(Order, order_id)
        product = db.session.get(Product, product_id)

        assert payment.status == "unknown"
        assert order.payment_status == "pending"
        assert product.stock == 8
@pytest.mark.parametrize(
    "receipt_value",
    [None, "", "   ", 123, []],
)
def test_invalid_mpesa_receipt_keeps_payment_pending(
    app, client, monkeypatch, receipt_value
):
    with app.app_context():
        order_id, payment_id, product_id = create_payment_order()

    monkeypatch.setattr(
        "routes.payments.query_stk_push",
        lambda checkout_id: successful_query()
    )

    callback = successful_callback()

    callback["Body"]["stkCallback"]["CallbackMetadata"]["Item"][1][
        "Value"
    ] = receipt_value

    response = client.post(
        "/api/payments/callback",
        json=callback
    )

    assert response.status_code == 200

    with app.app_context():
        payment = db.session.get(Payment, payment_id)
        order = db.session.get(Order, order_id)
        product = db.session.get(Product, product_id)

        assert payment.status == "unknown"
        assert payment.mpesa_receipt_number is None
        assert order.payment_status == "pending"
        assert product.stock == 8

def test_duplicate_successful_callback_sends_confirmation_once(
    app, client, monkeypatch
):
    with app.app_context():
        order_id, payment_id, product_id = create_payment_order()

    email_calls = []
    query_calls = []

    def mock_query(checkout_id):
        query_calls.append(checkout_id)
        return successful_query()

    monkeypatch.setattr(
        "routes.payments.query_stk_push",
        mock_query
    )
    monkeypatch.setattr(
        "routes.payments.send_order_confirmation",
        lambda order: (email_calls.append(order.id), True)[1]
    )

    callback = successful_callback()

    first_response = client.post(
        "/api/payments/callback",
        json=callback
    )
    second_response = client.post(
        "/api/payments/callback",
        json=callback
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert query_calls == ["checkout-123"]
    assert email_calls == [order_id]

    with app.app_context():
        payment = db.session.get(Payment, payment_id)
        order = db.session.get(Order, order_id)

        assert payment.status == "paid"
        assert order.payment_status == "paid"

def test_duplicate_mpesa_receipt_does_not_mark_second_order_paid(
    app, client, monkeypatch
):
    with app.app_context():
        first_order_id, first_payment_id, _ = create_payment_order()

        # Free the default request IDs for the second test payment.
        first_payment = db.session.get(Payment, first_payment_id)
        first_payment.merchant_request_id = "merchant-111"
        first_payment.checkout_request_id = "checkout-111"
        db.session.commit()

        second_order_id, second_payment_id, second_product_id = (
            create_payment_order()
        )

        # The first payment already owns this receipt.
        first_payment = db.session.get(Payment, first_payment_id)
        first_order = db.session.get(Order, first_order_id)

        first_payment.status = "paid"
        first_payment.mpesa_receipt_number = "TEST123456"
        first_order.payment_status = "paid"

        db.session.commit()

    # The default successful query and callback IDs now belong to
    # the second payment.
    monkeypatch.setattr(
        "routes.payments.query_stk_push",
        lambda checkout_id: successful_query()
    )

    response = client.post(
        "/api/payments/callback",
        json=successful_callback()
    )

    assert response.status_code == 200

    with app.app_context():
        first_payment = db.session.get(Payment, first_payment_id)
        second_payment = db.session.get(Payment, second_payment_id)
        second_order = db.session.get(Order, second_order_id)
        product = db.session.get(Product, second_product_id)

        assert first_payment.mpesa_receipt_number == "TEST123456"
        assert second_payment.status == "unknown"
        assert second_payment.mpesa_receipt_number is None
        assert second_order.payment_status == "pending"
        assert product.stock == 8

def test_stk_push_rejects_missing_csrf_token(app, client):
    with app.app_context():
        product_id, order_data = create_stk_request_data()

    response = client.post(
        "/api/payments/stk-push",
        json=order_data
    )

    assert response.status_code == 403

    with app.app_context():
        product = db.session.get(Product, product_id)

        assert Order.query.count() == 0
        assert Payment.query.count() == 0
        assert product.stock == 10