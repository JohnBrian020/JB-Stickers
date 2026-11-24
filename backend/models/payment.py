from datetime import datetime, timezone

from extensions import db


class Payment(db.Model):
    __tablename__ = "payments"

    __table_args__ = (
        db.UniqueConstraint(
            "mpesa_receipt_number",
            name="uq_payments_mpesa_receipt_number"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id"),
        nullable=False,
        index=True
    )

    phone_number = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)

    merchant_request_id = db.Column(db.String(100), nullable=True)
    checkout_request_id = db.Column(
        db.String(100),
        unique=True,
        nullable=True
    )

    mpesa_receipt_number = db.Column(
        db.String(50),
        nullable=True
    )
    result_code = db.Column(db.Integer, nullable=True)
    result_description = db.Column(db.Text, nullable=True)

    status = db.Column(
        db.String(20),
        nullable=False,
        default="initiated"
    )

    confirmation_email_status = db.Column(
        db.String(20),
        nullable=False,
        default="pending",
        server_default="pending"
    )

    confirmation_email_attempts = db.Column(
        db.Integer,
        nullable=False,
        default=0,
        server_default="0"
    )

    confirmation_email_sent_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )

    confirmation_email_last_error = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    order = db.relationship(
        "Order",
        back_populates="payments"
    )

    def __repr__(self):
        return f"<Payment {self.id}: {self.status}>"
