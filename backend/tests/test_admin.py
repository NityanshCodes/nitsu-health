"""Admin authorization + endpoints tests."""

from tests.conftest import auth, register_and_login


def test_non_admin_blocked(client, user_token):
    assert client.get("/admin/users", headers=auth(user_token)).status_code == 403
    assert client.get("/admin/subscriptions", headers=auth(user_token)).status_code == 403
    assert client.get("/admin/payments", headers=auth(user_token)).status_code == 403
    assert client.get("/admin/audit-log", headers=auth(user_token)).status_code == 403


def test_admin_can_view_users(client, admin_token):
    resp = client.get("/admin/users", headers=auth(admin_token))
    assert resp.status_code == 200
    assert "items" in resp.json()
    assert resp.json()["total"] >= 1


def test_admin_system_health(client, admin_token):
    resp = client.get("/admin/health", headers=auth(admin_token))
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_admin_requires_explicit_role(client, user_token):
    """An ordinary user must never be treated as admin via request manipulation."""
    # The admin endpoints rely on the DB role, not the request body.
    resp = client.get("/admin/users", headers=auth(user_token))
    assert resp.status_code == 403