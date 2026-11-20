import pytest


def get_csrf_headers(client):
    response = client.get("/api/auth/csrf-token")

    assert response.status_code == 200

    return {
        "X-CSRFToken": response.json["data"]["csrf_token"]
    }


def test_login_with_email(client, admin):
    response = client.post(
        "/api/auth/login",
        json={
            "identifier": "admin@example.com",
            "password": "TestPassword123!"
        },
        headers=get_csrf_headers(client)
    )

    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert response.json["data"]["username"] == "testadmin"
    assert response.json["data"]["csrf_token"]


def test_login_with_username(client, admin):
    response = client.post(
        "/api/auth/login",
        json={
            "identifier": "testadmin",
            "password": "TestPassword123!"
        },
        headers=get_csrf_headers(client)
    )

    assert response.status_code == 200
    assert response.json["status"] == "success"


def test_login_rejects_wrong_password(client, admin):
    response = client.post(
        "/api/auth/login",
        json={
            "identifier": "admin@example.com",
            "password": "WrongPassword123!"
        },
        headers=get_csrf_headers(client)
    )

    assert response.status_code == 401
    assert response.json["status"] == "error"


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"identifier": "admin@example.com"},
        {"password": "TestPassword123!"},
        {"identifier": "", "password": "TestPassword123!"},
    ]
)
def test_login_rejects_missing_credentials(client, payload):
    response = client.post(
        "/api/auth/login",
        json=payload,
        headers=get_csrf_headers(client)
    )

    assert response.status_code == 400
    assert response.json["status"] == "error"


def test_current_admin_requires_authentication(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_admin_dashboard_requires_authentication(client):
    response = client.get("/api/admin/dashboard")

    assert response.status_code == 401


def test_authenticated_admin_can_access_dashboard(client, admin):
    login_response = client.post(
        "/api/auth/login",
        json={
            "identifier": "testadmin",
            "password": "TestPassword123!"
        },
        headers=get_csrf_headers(client)
    )

    assert login_response.status_code == 200

    response = client.get("/api/admin/dashboard")

    assert response.status_code == 200
    assert response.json["status"] == "success"


def test_logout_invalidates_session(client, admin):
    login_response = client.post(
        "/api/auth/login",
        json={
            "identifier": "testadmin",
            "password": "TestPassword123!"
        },
        headers=get_csrf_headers(client)
    )

    assert login_response.status_code == 200

    # Login rotates the CSRF token. Use the new token for logout.
    csrf_token = login_response.json["data"]["csrf_token"]

    logout_response = client.post(
        "/api/auth/logout",
        headers={"X-CSRFToken": csrf_token}
    )

    assert logout_response.status_code == 200

    me_response = client.get("/api/auth/me")
    dashboard_response = client.get("/api/admin/dashboard")

    assert me_response.status_code == 401
    assert dashboard_response.status_code == 401


def test_login_rate_limit_blocks_sixth_attempt(client, admin):
    payload = {
        "identifier": "admin@example.com",
        "password": "WrongPassword123!"
    }

    headers = get_csrf_headers(client)

    for _ in range(5):
        response = client.post(
            "/api/auth/login",
            json=payload,
            headers=headers
        )

        assert response.status_code == 401

    response = client.post(
        "/api/auth/login",
        json=payload,
        headers=headers
    )

    assert response.status_code == 429
    assert response.json["status"] == "error"
    assert "Too many login attempts" in response.json["message"]


def test_login_rejects_missing_csrf_token(client, admin):
    response = client.post(
        "/api/auth/login",
        json={
            "identifier": "testadmin",
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 403
    assert response.json["status"] == "error"


def test_csrf_token_response_prevents_caching(client):
    response = client.get("/api/auth/csrf-token")

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["Pragma"] == "no-cache"


def test_login_rejects_untrusted_origin(client, admin):
    response = client.post(
        "/api/auth/login",
        json={
            "identifier": "testadmin",
            "password": "TestPassword123!"
        },
        headers={
            **get_csrf_headers(client),
            "Origin": "https://untrusted.example"
        }
    )

    assert response.status_code == 403
    assert response.json["status"] == "error"
    assert response.json["message"] == "Request origin is not allowed"


def test_login_accepts_trusted_origin(client, admin):
    response = client.post(
        "/api/auth/login",
        json={
            "identifier": "testadmin",
            "password": "TestPassword123!"
        },
        headers={
            **get_csrf_headers(client),
            "Origin": "http://localhost:5173"
        }
    )

    assert response.status_code == 200
    assert response.json["status"] == "success"
