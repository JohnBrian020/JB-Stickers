
from io import BytesIO

import pytest
from PIL import Image
from werkzeug.datastructures import FileStorage

import services.image_service as image_service


def make_image(image_format="PNG"):
    """Create a small valid image in memory."""
    buffer = BytesIO()
    Image.new("RGB", (10, 10), color="red").save(
        buffer,
        format=image_format
    )
    buffer.seek(0)
    return buffer


def make_upload(content, filename="test.png"):
    return FileStorage(
        stream=BytesIO(content),
        filename=filename
    )


def test_empty_image_is_rejected(app):
    with app.app_context():
        upload = make_upload(b"")

        with pytest.raises(ValueError, match="empty"):
            image_service.upload_product_image(upload)


def test_oversized_image_is_rejected(app):
    with app.app_context():
        content = b"x" * (5 * 1024 * 1024 + 1)
        upload = make_upload(content)

        with pytest.raises(ValueError, match="5 MB"):
            image_service.upload_product_image(upload)


def test_invalid_image_content_is_rejected(app):
    with app.app_context():
        upload = make_upload(
            b"This is not a valid image",
            filename="invalid.png"
        )

        with pytest.raises(ValueError, match="valid image"):
            image_service.upload_product_image(upload)


def test_unsupported_image_format_is_rejected(app):
    with app.app_context():
        image_buffer = make_image("GIF")
        upload = FileStorage(
            stream=image_buffer,
            filename="test.gif"
        )

        with pytest.raises(ValueError, match="Only JPG"):
            image_service.upload_product_image(upload)


def test_valid_image_is_uploaded_to_cloudinary(app, monkeypatch):
    with app.app_context():
        image_buffer = make_image("PNG")
        upload = FileStorage(
            stream=image_buffer,
            filename="test.png"
        )

        monkeypatch.setattr(
            image_service,
            "configure_cloudinary",
            lambda: None
        )

        monkeypatch.setattr(
            image_service.cloudinary.uploader,
            "upload",
            lambda *args, **kwargs: {
                "secure_url": "https://example.com/test.png",
                "public_id": "jb-stickers/products/test"
            }
        )

        result = image_service.upload_product_image(upload)

        assert result["image_url"] == "https://example.com/test.png"
        assert result["image_public_id"] == "jb-stickers/products/test"


def test_oversized_http_upload_returns_json_error(client, admin):
    # Get CSRF token.
    csrf_response = client.get("/api/auth/csrf-token")
    csrf_token = csrf_response.get_json()["data"]["csrf_token"]

    # Log in as test admin.
    login_response = client.post(
        "/api/auth/login",
        json={
            "identifier": "admin@example.com",
            "password": "TestPassword123!"
        },
        headers={"X-CSRFToken": csrf_token}
    )

    assert login_response.status_code == 200
    csrf_token = login_response.get_json()["data"]["csrf_token"]

    # Create a real product first.
    product_response = client.post(
        "/api/products",
        json={
            "name": "Test Sticker",
            "description": "Test product",
            "price": "100.00",
            "category": "Stickers",
            "stock": 10,
            "is_active": True
        },
        headers={"X-CSRFToken": csrf_token}
    )

    assert product_response.status_code == 201
    product_id = product_response.get_json()["data"]["id"]

    # Attempt an oversized upload.
    response = client.post(
        f"/api/products/{product_id}/image",
        data={
            "image": (
                BytesIO(b"x" * (5 * 1024 * 1024 + 1)),
                "large.png"
            )
        },
        headers={"X-CSRFToken": csrf_token},
        content_type="multipart/form-data"
    )

    assert response.status_code == 413
    assert response.is_json
    assert "too large" in response.get_json()["message"].lower()
