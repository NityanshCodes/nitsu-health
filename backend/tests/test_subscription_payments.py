"""Subscription + payments tests (demo provider)."""

from tests.conftest import auth


def test_default_subscription_is_free(client, user_token):
    status = client.get("/subscription/status", headers=auth(user_token)).json()
    assert status["plan"] == "FREE"
    assert status["status"] == "active"

    plan = client.get("/subscription/plan", headers=auth(user_token)).json()
    assert plan["plan"] == "FREE"
    # Basic features available on free plan
    assert plan["features"]["manual_data_entry"] is True
    # Premium-gated features not available
    assert plan["features"]["ai_reports"] is False


def test_payment_order_and_demo_verify(client, user_token):
    order = client.post(
        "/payments/create-order",
        headers=auth(user_token),
        json={"amount": 49900, "currency": "INR"},
    )
    assert order.status_code == 200
    order_id = order.json()["order_id"]
    assert order.json()["provider"] in ("demo", "razorpay")

    verify = client.post(
        "/payments/verify",
        headers=auth(user_token),
        json={
            "razorpay_order_id": order_id,
            "razorpay_payment_id": "pay_demo",
            "signature": "sig",
        },
    )
    # Demo verify accepts any non-empty signature
    assert verify.status_code == 200
    assert verify.json()["subscription"] == "PREMIUM"

    status = client.get("/subscription/status", headers=auth(user_token)).json()
    assert status["plan"] == "PREMIUM"


def test_payment_history(client, user_token):
    client.post("/payments/create-order", headers=auth(user_token), json={"amount": 49900})
    history = client.get("/payments/history", headers=auth(user_token)).json()
    assert len(history["payments"]) == 1
    assert history["payments"][0]["status"] == "created"


def test_downgrade(client, user_token):
    client.post("/subscription/downgrade", headers=auth(user_token))
    status = client.get("/subscription/status", headers=auth(user_token)).json()
    assert status["plan"] == "FREE"