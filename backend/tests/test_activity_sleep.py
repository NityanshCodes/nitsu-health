"""Activity + Sleep CRUD tests."""

from datetime import datetime

from tests.conftest import auth

ACTIVITY = {
    "activity_type": "walking",
    "steps": 8000,
    "active_minutes": 60,
    "distance_km": 5.2,
    "calories_burned": 300,
}

SLEEP = {
    "start_time": "2026-09-07T22:00:00",
    "end_time": "2026-09-08T06:30:00",
}


def test_activity_crud(client, user_token):
    created = client.post("/activity", headers=auth(user_token), json=ACTIVITY)
    assert created.status_code == 201
    entry_id = created.json()["id"]

    assert client.get(f"/activity/{entry_id}", headers=auth(user_token)).json()["steps"] == 8000

    updated = client.put(
        f"/activity/{entry_id}",
        headers=auth(user_token),
        json={"steps": 10000},
    )
    assert updated.json()["steps"] == 10000

    assert client.delete(f"/activity/{entry_id}", headers=auth(user_token)).status_code == 204
    assert client.get(f"/activity/{entry_id}", headers=auth(user_token)).status_code == 404


def test_activity_today_summary(client, user_token):
    client.post("/activity", headers=auth(user_token), json=ACTIVITY)
    today = client.get("/activity/today", headers=auth(user_token)).json()
    assert today["total_steps"] == 8000
    assert today["total_calories_burned"] == 300.0


def test_activity_user_scoped(client, user_token):
    from tests.conftest import register_and_login

    other_token = register_and_login(client, "otheract@example.com", "otheract")
    entry = client.post("/activity", headers=auth(user_token), json=ACTIVITY).json()
    assert client.delete(f"/activity/{entry['id']}", headers=auth(other_token)).status_code == 404


def test_sleep_crud(client, user_token):
    created = client.post("/sleep", headers=auth(user_token), json=SLEEP)
    assert created.status_code == 201
    entry_id = created.json()["id"]

    fetched = client.get(f"/sleep/{entry_id}", headers=auth(user_token))
    assert fetched.status_code == 200
    assert fetched.json()["start_time"]

    assert client.delete(f"/sleep/{entry_id}", headers=auth(user_token)).status_code == 204

    empty = client.get("/sleep", headers=auth(user_token)).json()
    assert empty["total"] == 0


def test_sleep_user_scoped(client, user_token):
    from tests.conftest import register_and_login

    other_token = register_and_login(client, "othersleep@example.com", "othersleep")
    entry = client.post("/sleep", headers=auth(user_token), json=SLEEP).json()
    assert client.get(f"/sleep/{entry['id']}", headers=auth(other_token)).status_code == 404
    assert client.delete(f"/sleep/{entry['id']}", headers=auth(other_token)).status_code == 404