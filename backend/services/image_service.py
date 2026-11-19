from io import BytesIO

import cloudinary
import cloudinary.uploader
from flask import current_app
from PIL import Image, UnidentifiedImageError


ALLOWED_IMAGE_FORMATS = {
    "JPEG",
    "PNG",
    "WEBP",
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024


def configure_cloudinary():
    cloud_name = current_app.config.get("CLOUDINARY_CLOUD_NAME")
    api_key = current_app.config.get("CLOUDINARY_API_KEY")
    api_secret = current_app.config.get("CLOUDINARY_API_SECRET")

    if not all([cloud_name, api_key, api_secret]):
        raise RuntimeError("Cloudinary is not fully configured.")

    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True,
    )


def upload_product_image(image_file):
    if image_file is None or not image_file.filename:
        raise ValueError("Please select an image to upload.")

    image_data = image_file.read()

    if not image_data:
        raise ValueError("The selected image is empty.")

    if len(image_data) > MAX_IMAGE_SIZE:
        raise ValueError("Image size must not exceed 5 MB.")

    try:
        with Image.open(BytesIO(image_data)) as image:
            if image.format not in ALLOWED_IMAGE_FORMATS:
                raise ValueError(
                    "Only JPG, JPEG, PNG and WebP images are allowed."
                )

            image.verify()

    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise ValueError("The uploaded file is not a valid image.")

    configure_cloudinary()

    result = cloudinary.uploader.upload(
        image_data,
        folder="jb-stickers/products",
        resource_type="image",
        transformation=[
            {
                "quality": "auto",
                "fetch_format": "auto",
            }
        ],
    )

    return {
        "image_url": result["secure_url"],
        "image_public_id": result["public_id"],
    }


def delete_cloudinary_image(public_id):
    if not public_id:
        return

    configure_cloudinary()

    return cloudinary.uploader.destroy(
        public_id,
        resource_type="image",
    )
