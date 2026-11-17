from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from utils.decorators import admin_required

from schemas.product_schema import ProductSchema
from services.product_service import (
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product
)
from utils.responses import success_response, error_response


products_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/api/products"
)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)


@products_bp.route("", methods=["GET"])
def list_products():
    search = request.args.get("search")
    category = request.args.get("category")

    products = get_all_products(
        search=search,
        category=category
    )

    return success_response(
        data=products_schema.dump(products),
        message="Products retrieved successfully"
    )


@products_bp.route("/<int:product_id>", methods=["GET"])
def retrieve_product(product_id):
    product = get_product_by_id(product_id)

    if product is None or not product.is_active:
        return error_response("Product not found", 404)

    return success_response(
        data=product_schema.dump(product),
        message="Product retrieved successfully"
    )


@products_bp.route("", methods=["POST"])
@admin_required
def add_product():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_response("A valid JSON object is required")

    try:
        product_data = product_schema.load(data)
        product = create_product(product_data)

        return success_response(
            data=product_schema.dump(product),
            message="Product created successfully",
            status=201
        )

    except ValidationError as error:
        return error_response(
            "Product validation failed",
            400,
            error.messages
        )

    except IntegrityError:
        from extensions import db
        db.session.rollback()
        return error_response("Could not create product", 400)


@products_bp.route("/<int:product_id>", methods=["PATCH"])
@admin_required
def edit_product(product_id):
    product = get_product_by_id(product_id)

    if product is None:
        return error_response("Product not found", 404)

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return error_response("Provide product fields to update")

    try:
        product_data = product_schema.load(data, partial=True)

        product = update_product(product, product_data)

        return success_response(
            data=product_schema.dump(product),
            message="Product updated successfully"
        )

    except ValidationError as error:
        return error_response(
            "Product validation failed",
            400,
            error.messages
        )

    except IntegrityError:
        from extensions import db
        db.session.rollback()
        return error_response("Could not update product", 400)


@products_bp.route("/<int:product_id>", methods=["DELETE"])
@admin_required
def remove_product(product_id):
    product = get_product_by_id(product_id)

    if product is None:
        return error_response("Product not found", 404)

    try:
        delete_product(product)

        return success_response(
            message="Product deleted successfully"
        )

    except ValueError as error:
        return error_response(str(error), 409)
