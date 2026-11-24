import base64
from datetime import datetime
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

import requests
from flask import current_app


REQUEST_TIMEOUT = 20


class MPesaRejectedError(RuntimeError):
    """Safaricom explicitly rejected an STK Push request."""


class MPesaNotSentError(RuntimeError):
    """The STK Push request was not sent to Safaricom."""


class MPesaUncertainError(RuntimeError):
    """STK Push may have reached Safaricom, but its result is unknown."""


def normalize_phone_number(phone):
    """Convert Kenyan phone numbers to Safaricom's 254 format."""

    if not isinstance(phone, str):
        raise ValueError("A valid Kenyan phone number is required.")

    phone = phone.strip().replace(" ", "").replace("-", "")

    if phone.startswith("+"):
        phone = phone[1:]

    if phone.startswith("0") and len(phone) == 10:
        phone = "254" + phone[1:]

    elif phone.startswith("7") or phone.startswith("1"):
        if len(phone) == 9:
            phone = "254" + phone

    if (
        len(phone) != 12
        or not phone.isdigit()
        or not phone.startswith(("2547", "2541"))
    ):
        raise ValueError(
            "Enter a valid Kenyan mobile number, e.g. 0712345678."
        )

    return phone


def get_mpesa_access_token():
    """Authenticate with Safaricom Daraja and return an access token."""

    consumer_key = current_app.config.get("MPESA_CONSUMER_KEY")
    consumer_secret = current_app.config.get("MPESA_CONSUMER_SECRET")
    base_url = current_app.config.get("MPESA_BASE_URL")

    if not consumer_key or not consumer_secret:
        raise RuntimeError("M-Pesa API credentials are not configured.")

    try:
        response = requests.get(
            f"{base_url}/oauth/v1/generate",
            params={"grant_type": "client_credentials"},
            auth=(consumer_key, consumer_secret),
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()
        data = response.json()

        access_token = data.get("access_token")

        if not access_token:
            raise RuntimeError("Safaricom did not return an access token.")

        return access_token

    except requests.RequestException as error:
        current_app.logger.error(
            "Daraja authentication request failed: %s",
            error
        )
        raise RuntimeError(
            "Could not authenticate with M-Pesa. Please try again."
        ) from error


def initiate_stk_push(phone_number, amount, order_id):
    """Send an STK Push request for an order."""

    config = current_app.config

    environment = config.get("MPESA_ENV", "sandbox")
    if environment not in {"sandbox", "production"}:
        raise MPesaNotSentError("Invalid M-Pesa environment configuration.")

    shortcode = config.get("MPESA_SHORTCODE")
    passkey = config.get("MPESA_PASSKEY")
    callback_url = config.get("MPESA_CALLBACK_URL")
    transaction_type = config.get(
        "MPESA_TRANSACTION_TYPE",
        "CustomerPayBillOnline"
    )
    base_url = config.get("MPESA_BASE_URL")

    if not all((shortcode, passkey, callback_url, base_url)):
        raise MPesaNotSentError("M-Pesa STK Push configuration is incomplete.")

    if not callback_url.startswith("https://"):
        raise MPesaNotSentError("The M-Pesa callback URL must use HTTPS.")

    phone = normalize_phone_number(phone_number)

    try:
        decimal_amount = Decimal(str(amount))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError("Invalid payment amount.") from error

    if (
        not decimal_amount.is_finite()
        or decimal_amount <= 0
        or decimal_amount != decimal_amount.to_integral_value()
    ):
        raise ValueError(
            "M-Pesa payments must use a positive whole-number KSh amount."
        )

    amount_int = int(decimal_amount)

    # Daraja requires the timestamp in East Africa Time.
    timestamp = datetime.now(
        ZoneInfo("Africa/Nairobi")
    ).strftime("%Y%m%d%H%M%S")

    password_string = f"{shortcode}{passkey}{timestamp}"

    password = base64.b64encode(
        password_string.encode("utf-8")
    ).decode("utf-8")

    try:
        access_token = get_mpesa_access_token()
    except Exception as error:
        current_app.logger.exception(
            "M-Pesa authentication failed before STK Push for order %s",
            order_id
        )
        raise MPesaNotSentError(
            "Could not authenticate with M-Pesa. No payment request was sent."
        ) from error

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": transaction_type,
        "Amount": amount_int,
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": callback_url,
        "AccountReference": "JBSTICKERS",
        "TransactionDesc": f"Order {order_id}"
    }

    try:
        response = requests.post(
            f"{base_url}/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()
        data = response.json()

    except Exception as error:
        current_app.logger.exception(
            "STK Push result is uncertain for order %s",
            order_id
        )
        raise MPesaUncertainError(
            "Safaricom's response could not be confirmed. "
            "Do not submit another payment request yet."
        ) from error

    if not isinstance(data, dict):
        raise MPesaUncertainError(
            "Safaricom returned an invalid STK Push response."
        )

    if str(data.get("ResponseCode")) != "0":
        description = data.get(
            "ResponseDescription",
            "Safaricom rejected the payment request."
        )

        current_app.logger.warning(
            "Daraja rejected STK Push for order %s: %s",
            order_id,
            description
        )

        raise MPesaRejectedError(description)

    merchant_request_id = data.get("MerchantRequestID")
    checkout_request_id = data.get("CheckoutRequestID")

    if not merchant_request_id or not checkout_request_id:
        raise MPesaUncertainError(
            "Safaricom did not return the required payment reference IDs."
        )

    return {
        "merchant_request_id": data.get("MerchantRequestID"),
        "checkout_request_id": data.get("CheckoutRequestID"),
        "response_description": data.get("ResponseDescription"),
        "customer_message": data.get("CustomerMessage")
    }


def query_stk_push(checkout_request_id):
    """Ask Safaricom for the actual status of an STK Push transaction."""

    config = current_app.config

    shortcode = config.get("MPESA_SHORTCODE")
    passkey = config.get("MPESA_PASSKEY")
    base_url = config.get("MPESA_BASE_URL")

    if not all((shortcode, passkey, base_url, checkout_request_id)):
        raise RuntimeError("M-Pesa query configuration is incomplete.")

    timestamp = datetime.now(
        ZoneInfo("Africa/Nairobi")
    ).strftime("%Y%m%d%H%M%S")

    password = base64.b64encode(
        f"{shortcode}{passkey}{timestamp}".encode("utf-8")
    ).decode("utf-8")

    access_token = get_mpesa_access_token()

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "CheckoutRequestID": checkout_request_id
    }

    try:
        response = requests.post(
            f"{base_url}/mpesa/stkpushquery/v1/query",
            json=payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()
        return response.json()

    except requests.RequestException as error:
        current_app.logger.exception(
            "STK Push query failed for checkout request %s",
            checkout_request_id
        )
        raise RuntimeError(
            "Could not verify the M-Pesa transaction with Safaricom."
        ) from error
