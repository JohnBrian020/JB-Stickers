from flask import Blueprint, request, current_app
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from extensions import db
from utils.decorators import admin_required
from schemas.product_schema import ProductSchema

from services.product_service import (
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product
)

from services.image_service import (
    upload_product_image,
    delete_cloudinary_image
)

from utils.responses import success_response, error_response

products_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/api/products"
)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

@products_bp.route("/admin", methods=["GET"])
@admin_required
def list_admin_products():
    products = get_all_products(include_inactive=True)

    return success_response(
        data=products_schema.dump(products),
        message="Admin products retrieved successfully"
    )

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
        current_app.logger.exception(
            "Database integrity error while creating product"
        )
        return error_response("Could not create product", 400)

    except Exception:
        current_app.logger.exception(
            "Unexpected error while creating product"
        )
        return error_response("Could not create product", 500)

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
        current_app.logger.exception(
            "Database integrity error while updating product"
        )
        return error_response("Could not update product", 400)

    except Exception:
        current_app.logger.exception(
            "Unexpected error while updating product"
        )
        return error_response("Could not update product", 500)


@products_bp.route("/<int:product_id>", methods=["DELETE"])
@admin_required
def remove_product(product_id):
    product = get_product_by_id(product_id)

    if product is None:
        return error_response("Product not found", 404)

    image_public_id = product.image_public_id

    try:
        delete_product(product)

    except ValueError as error:
        return error_response(str(error), 409)

    except Exception:
        current_app.logger.exception(
            "Failed to delete product from database"
        )
        return error_response("Could not delete product", 500)

    if image_public_id:
        try:
            deletion_result = delete_cloudinary_image(image_public_id)

            if deletion_result.get("result") == "ok":
                current_app.logger.info(
                    "Cloudinary image deleted after product deletion."
                )

            elif deletion_result.get("result") == "not found":
                current_app.logger.warning(
                    "Cloudinary image was not found: %s",
                    image_public_id
                )

            else:
                current_app.logger.warning(
                    "Unexpected Cloudinary deletion response: %s",
                    deletion_result
                )

        except Exception:
            current_app.logger.exception(
                "Product deleted, but Cloudinary image cleanup failed."
            )

    return success_response(
        message="Product deleted successfully"
    )

@products_bp.route("/<int:product_id>/image", methods=["POST"])
@admin_required
def upload_product_image_route(product_id):
    product = get_product_by_id(product_id)

    if product is None:
        return error_response("Product not found", 404)

    image_file = request.files.get("image")

    if image_file is None:
        return error_response("Please select an image to upload", 400)

    try:
        upload_result = upload_product_image(image_file)

    except ValueError as error:
        return error_response(str(error), 400)

    except Exception:
        current_app.logger.exception(
            "Cloudinary product image upload failed"
        )
        return error_response("Image upload failed. Please try again.", 502)

    previous_public_id = product.image_public_id

    product.image_url = upload_result["image_url"]
    product.image_public_id = upload_result["image_public_id"]

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()

        try:
            delete_cloudinary_image(
                upload_result["image_public_id"]
            )
        except Exception:
            current_app.logger.exception(
                "Failed to clean up uploaded image after database failure"
            )

        return error_response(
            "Could not save the product image. Please try again.",
            500
        )

    # Delete the previous image only after the new image is saved.
    if previous_public_id:
        try:
            deletion_result = delete_cloudinary_image(previous_public_id)

            if deletion_result.get("result") == "ok":
                current_app.logger.info(
                    "Previous Cloudinary product image deleted successfully."
                )

            elif deletion_result.get("result") == "not found":
                current_app.logger.warning(
                    "Previous Cloudinary product image was not found: %s",
                    previous_public_id
                )

            else:
                current_app.logger.warning(
                    "Unexpected Cloudinary deletion response: %s",
                    deletion_result
                )

        except Exception:
            current_app.logger.exception(
                "Failed to delete previous Cloudinary product image"
            )

    return success_response(
        data=product_schema.dump(product),
        message="Product image uploaded successfully"
    )