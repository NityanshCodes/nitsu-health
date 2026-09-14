"""Dashboard endpoint tests."""

from tests.conftest import auth


def test_dashboard_returns_overview(client, user_token):
    resp = client.get("/dashboard", headers=auth(user_token))
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["user_id"] == 1
    assert "nutrition_today" in payload
    assert "active_goals" in payload
    assert "unread_notifications" in payload


def test_dashboard_scopes_to_user(client, user_token):
    from tests.conftest import register_and_login

    other_token = register_and_login(client, "other@example.com", "otheruser")
    # Seed nutrition for the first user only
    resp = client.post(
        "/nutrition",
        headers=auth(user_token),
        json={
            "meal_type": "breakfast",
            "calories": 700,
            "protein_g": 30,
            "carbs_g": 80,
            "fats_g": 20,
            "water_ml": 300,
        },
    )
    assert resp.status_code == 201

    mine = client.get("/dashboard", headers=auth(user_token)).json()
    theirs = client.get("/dashboard", headers=auth(other_token)).json()
    assert mine["nutrition_today"]["calories"] == 700
    assert theirs["nutrition_today"]["calories"] == 0