from marshmallow import Schema, fields, validate

from schemas.customer_schema import CustomerSchema


class OrderItemInputSchema(Schema):
    product_id = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )

    quantity = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )


class OrderInputSchema(Schema):
    customer = fields.Nested(
        CustomerSchema,
        required=True
    )

    items = fields.List(
        fields.Nested(OrderItemInputSchema),
        required=True,
        validate=validate.Length(min=1)
    )