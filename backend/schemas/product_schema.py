from decimal import Decimal

from marshmallow import Schema, fields, validate


class ProductSchema(Schema):
    id = fields.Int(dump_only=True)

    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=120)
    )

    description = fields.Str(allow_none=True)

    price = fields.Decimal(
        required=True,
        as_string=True,
        places=2,
        validate=validate.Range(min=Decimal("0.01"))
    )

    image_url = fields.Str(allow_none=True)
    category = fields.Str(allow_none=True)

    stock = fields.Int(
        load_default=0,
        validate=validate.Range(min=0)
    )

    is_active = fields.Bool(load_default=True)

    created_at = fields.DateTime(dump_only=True)
