import pytest
from marshmallow import ValidationError

from schemas.product_schema import ProductSchema


@pytest.fixture
def schema():
    return ProductSchema()


def valid_product_data():
    return {
        "name": "Classic Sticker",
        "description": "A quality vinyl sticker",
        "price": "100.00",
        "category": "Stickers",
        "stock": 10,
        "is_active": True
    }


def test_valid_product_data_is_accepted(schema):
    data = schema.load(valid_product_data())

    assert data["name"] == "Classic Sticker"
    assert data["price"] == 100
    assert data["stock"] == 10


@pytest.mark.parametrize("name", ["", " ", "   ", "\t"])
def test_empty_or_whitespace_product_name_is_rejected(schema, name):
    data = valid_product_data()
    data["name"] = name

    with pytest.raises(ValidationError):
        schema.load(data)


@pytest.mark.parametrize("price", ["0", "-10", "0.00"])
def test_invalid_product_price_is_rejected(schema, price):
    data = valid_product_data()
    data["price"] = price

    with pytest.raises(ValidationError):
        schema.load(data)


def test_negative_stock_is_rejected(schema):
    data = valid_product_data()
    data["stock"] = -1

    with pytest.raises(ValidationError):
        schema.load(data)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("description", "x" * 2001),
        ("category", "x" * 81),
        ("image_url", "x" * 501),
    ]
)
def test_excessively_long_fields_are_rejected(schema, field, value):
    data = valid_product_data()
    data[field] = value

    with pytest.raises(ValidationError):
        schema.load(data)


def test_unknown_fields_are_rejected(schema):
    data = valid_product_data()
    data["unexpected_field"] = "unexpected value"

    with pytest.raises(ValidationError):
        schema.load(data)


def test_dump_only_fields_cannot_be_submitted(schema):
    data = valid_product_data()
    data["id"] = 999

    with pytest.raises(ValidationError):
        schema.load(data)
