"""User endpoints tests."""

from tests.conftest import auth


def test_user_me(client, user_token):
    resp = client.get("/users/me", headers=auth(user_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"]
    assert data["role"] == "USER"
    assert data["is_active"] is True


def test_change_password(client, user_token):
    resp = client.patch(
        "/users/me/password",
        headers=auth(user_token),
        json={"current_password": "StrongPass123!", "new_password": "NewPass456!"},
    )
    assert resp.status_code == 200
    assert resp.json()["message"]

    # Old password rejected
    resp = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "StrongPass123!"},
    )
    assert resp.status_code in (401, 422)

    # New password works
    resp = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "NewPass456!"},
    )
    assert resp.status_code == 200