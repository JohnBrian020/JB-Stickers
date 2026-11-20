from decimal import Decimal

from marshmallow import Schema, fields, validate, validates, ValidationError


class ProductSchema(Schema):
    id = fields.Int(dump_only=True)

    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=120)
    )

    description = fields.Str(
        allow_none=True,
        validate=validate.Length(max=2000)
    )

    price = fields.Decimal(
        required=True,
        as_string=True,
        places=2,
        validate=validate.Range(min=Decimal("0.01"))
    )

    image_url = fields.Str(
        allow_none=True,
        validate=validate.Length(max=500)
    )

    category = fields.Str(
        allow_none=True,
        validate=validate.Length(max=80)
    )

    stock = fields.Int(
        load_default=0,
        validate=validate.Range(min=0)
    )

    is_active = fields.Bool(load_default=True)

    created_at = fields.DateTime(dump_only=True)

    @validates("name")
    def validate_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Product name cannot be empty.")

    class Meta:
        unknown = "raise"