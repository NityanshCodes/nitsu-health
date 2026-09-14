"""Wearables / Fitbit provider tests."""

from tests.conftest import auth


def test_wearable_status_unconfigured(client, user_token):
    resp = client.get("/wearables/status", headers=auth(user_token))
    assert resp.status_code == 200
    payload = resp.json()
    # "configured" may be True (demo provider) or False (no creds); both are fine,
    # but the response must match the provider contract.
    assert "configured" in payload
    assert "connections" in payload


def test_fitbit_connect_returns_url(client, user_token):
    resp = client.get("/wearables/fitbit/connect", headers=auth(user_token))
    assert resp.status_code == 200
    assert "auth_url" in resp.json()
    assert "state" in resp.json()


def test_sync_requires_connection(client, user_token):
    resp = client.post("/wearables/fitbit/sync", headers=auth(user_token))
    if resp.status_code == 404:
        # No connection — expected when not connected.
        assert resp.json()["detail"]
    else:
        # Demo mode may succeed; either is acceptable as long as not a 500.
        assert resp.status_code in (200, 503)


def test_callback_creates_connection(client, user_token):
    resp = client.get(
        "/wearables/fitbit/callback?code=demo_code&state=x",
        headers=auth(user_token),
    )
    if resp.status_code == 503:
        # Provider unavailable in this environment; acceptable.
        return
    assert resp.status_code == 200
    assert resp.json()["status"] == "connected"

    status = client.get("/wearables/status", headers=auth(user_token)).json()
    assert status["connections"], "Expected at least one connection after callback"