"""Nutrition CRUD + true daily aggregation tests."""

from tests.conftest import auth

MEAL = {
    "meal_type": "lunch",
    "calories": 600,
    "protein_g": 25,
    "carbs_g": 75,
    "fats_g": 20,
    "fiber_g": 5,
    "water_ml": 500,
}


def test_create_and_get_nutrition(client, user_token):
    created = client.post("/nutrition", headers=auth(user_token), json=MEAL)
    assert created.status_code == 201
    entry_id = created.json()["id"]

    fetched = client.get(f"/nutrition/{entry_id}", headers=auth(user_token))
    assert fetched.status_code == 200
    assert fetched.json()["calories"] == 600


def test_daily_summary_sums_all_entries(client, user_token):
    client.post("/nutrition", headers=auth(user_token), json=MEAL)
    client.post(
        "/nutrition",
        headers=auth(user_token),
        json={**MEAL, "meal_type": "dinner", "calories": 400, "water_ml": 0},
    )
    summary = client.get("/nutrition/today", headers=auth(user_token)).json()
    assert summary["calories"] == 1000
    assert summary["entries"] == 2
    assert summary["calories"] == 1000.0


def test_update_and_delete_nutrition(client, user_token):
    entry = client.post("/nutrition", headers=auth(user_token), json=MEAL).json()
    updated = client.put(
        f"/nutrition/{entry['id']}",
        headers=auth(user_token),
        json={"calories": 700},
    )
    assert updated.status_code == 200
    assert updated.json()["calories"] == 700

    deleted = client.delete(f"/nutrition/{entry['id']}", headers=auth(user_token))
    assert deleted.status_code == 204

    gone = client.get(f"/nutrition/{entry['id']}", headers=auth(user_token))
    assert gone.status_code == 404


def test_nutrition_is_user_scoped(client, user_token):
    from tests.conftest import register_and_login

    other_token = register_and_login(client, "other2@example.com", "otheruser2")
    entry = client.post("/nutrition", headers=auth(user_token), json=MEAL).json()

    # Other user cannot read or modify this entry
    assert client.get(f"/nutrition/{entry['id']}", headers=auth(other_token)).status_code == 404
    assert client.put(f"/nutrition/{entry['id']}", headers=auth(other_token), json={"calories": 1}).status_code == 404
    assert client.delete(f"/nutrition/{entry['id']}", headers=auth(other_token)).status_code == 404


def test_nutrition_trend(client, user_token):
    client.post("/nutrition", headers=auth(user_token), json=MEAL)
    trend = client.get("/nutrition/trends?metric=calories&days=7", headers=auth(user_token))
    assert trend.status_code == 200
    assert "days" in trend.json()

    bad = client.get("/nutrition/trends?metric=nope", headers=auth(user_token))
    assert bad.status_code == 422