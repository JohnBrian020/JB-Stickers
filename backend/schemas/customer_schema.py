from marshmallow import Schema, fields, validate


class CustomerSchema(Schema):
    id = fields.Int(dump_only=True)

    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=120)
    )

    email = fields.Email(required=True)

    phone = fields.Str(
        required=True,
        validate=validate.Length(min=7, max=30)
    )

    address = fields.Str(
        required=True,
        validate=validate.Length(min=5)
    )