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


def login_test_admin(client):
    csrf_headers = get_csrf_headers(client)

    return client.post(
        "/api/auth/login",
        json={
            "identifier": "testadmin",
            "password": "TestPassword123!"
        },
        headers=csrf_headers
    )


def test_profile_update_changes_username_and_email(client, admin):
    login_response = login_test_admin(client)
    assert login_response.status_code == 200

    csrf_token = login_response.json["data"]["csrf_token"]

    response = client.patch(
        "/api/auth/profile",
        json={
            "username": "updatedadmin",
            "email": "updated@example.com",
            "current_password": "TestPassword123!"
        },
        headers={"X-CSRFToken": csrf_token}
    )

    assert response.status_code == 200
    assert response.json["data"]["username"] == "updatedadmin"
    assert response.json["data"]["email"] == "updated@example.com"
    assert "password_hash" not in response.json["data"]

    me_response = client.get("/api/auth/me")
    assert me_response.status_code == 200
    assert me_response.json["data"]["username"] == "updatedadmin"


def test_profile_update_rejects_wrong_current_password(client, admin):
    login_response = login_test_admin(client)
    csrf_token = login_response.json["data"]["csrf_token"]

    response = client.patch(
        "/api/auth/profile",
        json={
            "username": "updatedadmin",
            "current_password": "WrongPassword123!"
        },
        headers={"X-CSRFToken": csrf_token}
    )

    assert response.status_code == 401


def test_profile_update_rejects_invalid_email(client, admin):
    login_response = login_test_admin(client)
    csrf_token = login_response.json["data"]["csrf_token"]

    response = client.patch(
        "/api/auth/profile",
        json={
            "email": "not-an-email",
            "current_password": "TestPassword123!"
        },
        headers={"X-CSRFToken": csrf_token}
    )

    assert response.status_code == 400


def test_profile_update_rejects_duplicate_username(
    client,
    app,
    admin
):
    from extensions import db, bcrypt
    from models import Admin

    with app.app_context():
        other_admin = Admin(
            username="anotheradmin",
            email="another@example.com",
            password_hash=bcrypt.generate_password_hash(
                "AnotherPassword123!"
            ).decode("utf-8")
        )
        db.session.add(other_admin)
        db.session.commit()

    login_response = login_test_admin(client)
    csrf_token = login_response.json["data"]["csrf_token"]

    response = client.patch(
        "/api/auth/profile",
        json={
            "username": "anotheradmin",
            "current_password": "TestPassword123!"
        },
        headers={"X-CSRFToken": csrf_token}
    )

    assert response.status_code == 409


def test_profile_update_requires_authentication(client):
    response = client.patch(
        "/api/auth/profile",
        json={
            "username": "updatedadmin",
            "current_password": "TestPassword123!"
        },
        headers=get_csrf_headers(client)
    )

    assert response.status_code == 401


def test_password_update_requires_current_password(client, admin):
    login_response = login_test_admin(client)
    csrf_token = login_response.json["data"]["csrf_token"]

    response = client.patch(
        "/api/auth/password",
        json={
            "current_password": "WrongPassword123!",
            "new_password": "NewSecurePassword123!"
        },
        headers={"X-CSRFToken": csrf_token}
    )

    assert response.status_code == 401


def test_password_update_rejects_short_password(client, admin):
    login_response = login_test_admin(client)
    csrf_token = login_response.json["data"]["csrf_token"]

    response = client.patch(
        "/api/auth/password",
        json={
            "current_password": "TestPassword123!",
            "new_password": "short"
        },
        headers={"X-CSRFToken": csrf_token}
    )

    assert response.status_code == 400


def test_password_update_changes_password_and_invalidates_sessions(
    client,
    admin
):
    login_response = login_test_admin(client)
    assert login_response.status_code == 200

    old_session_cookie = client.get_cookie("session")
    csrf_token = login_response.json["data"]["csrf_token"]

    # Simulate another browser using the old authenticated session.
    second_client = client.application.test_client()
    second_client.set_cookie("session", old_session_cookie.value)

    response = client.patch(
        "/api/auth/password",
        json={
            "current_password": "TestPassword123!",
            "new_password": "NewSecurePassword123!"
        },
        headers={"X-CSRFToken": csrf_token}
    )

    assert response.status_code == 200
    assert response.json["data"]["csrf_token"]

    # Both old sessions must now be invalid.
    assert client.get("/api/auth/me").status_code == 401
    assert second_client.get("/api/auth/me").status_code == 401

    # The new password must work.
    new_login = client.post(
        "/api/auth/login",
        json={
            "identifier": "testadmin",
            "password": "NewSecurePassword123!"
        },
        headers=get_csrf_headers(client)
    )

    assert new_login.status_code == 200

    # The previous password must no longer work.
    old_login = second_client.post(
        "/api/auth/login",
        json={
            "identifier": "testadmin",
            "password": "TestPassword123!"
        },
        headers=get_csrf_headers(second_client)
    )

    assert old_login.status_code == 401


def test_password_update_rejects_missing_csrf(client, admin):
    login_response = login_test_admin(client)
    assert login_response.status_code == 200

    response = client.patch(
        "/api/auth/password",
        json={
            "current_password": "TestPassword123!",
            "new_password": "NewSecurePassword123!"
        }
    )

    assert response.status_code == 403
