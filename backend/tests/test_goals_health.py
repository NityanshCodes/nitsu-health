"""Health metrics + goals CRUD tests."""

from tests.conftest import auth


def test_health_metric_crud(client, user_token):
    payload = {"metric_type": "weight", "value": 72.5, "unit": "kg"}
    created = client.post("/health/metrics", headers=auth(user_token), json=payload)
    assert created.status_code == 201
    metric_id = created.json()["id"]

    listed = client.get("/health/metrics", headers=auth(user_token)).json()
    assert listed["total"] == 1
    assert listed["items"][0]["metric_type"] == "weight"

    updated = client.put(
        f"/health/metrics/{metric_id}",
        headers=auth(user_token),
        json={"value": 71.0},
    )
    assert updated.json()["value"] == 71.0

    assert client.delete(f"/health/metrics/{metric_id}", headers=auth(user_token)).status_code == 204
    assert client.get(f"/health/metrics/{metric_id}", headers=auth(user_token)).status_code == 404


def test_metric_rejects_bad_value(client, user_token):
    bad = client.post(
        "/health/metrics",
        headers=auth(user_token),
        json={"metric_type": "weight", "value": -5, "unit": "kg"},
    )
    assert bad.status_code == 422


def test_health_metric_user_scoped(client, user_token):
    from tests.conftest import register_and_login

    other_token = register_and_login(client, "othermetric@example.com", "othermetric")
    metric = client.post(
        "/health/metrics",
        headers=auth(user_token),
        json={"metric_type": "heart_rate", "value": 68, "unit": "bpm"},
    ).json()
    assert client.get(f"/health/metrics/{metric['id']}", headers=auth(other_token)).status_code == 404


GOAL = {
    "goal_type": "steps",
    "title": "Walk 10k steps daily",
    "target_value": 10000,
    "unit": "steps",
    "start_date": "2026-09-01",
    "target_date": "2026-10-01",
    "progress_value": 2000,
}


def test_goal_crud_and_progress(client, user_token):
    created = client.post("/goals", headers=auth(user_token), json=GOAL)
    assert created.status_code == 201
    goal_id = created.json()["id"]
    assert created.json()["status"] == "active"

    progressed = client.post(
        f"/goals/{goal_id}/progress",
        headers=auth(user_token),
        json={"progress_value": 10000},
    )
    assert progressed.json()["status"] == "completed"
    assert progressed.json()["completed_at"] is not None

    assert client.delete(f"/goals/{goal_id}", headers=auth(user_token)).status_code == 204


def test_goal_list_by_status(client, user_token):
    client.post("/goals", headers=auth(user_token), json=GOAL)
    active = client.get("/goals?status=active", headers=auth(user_token)).json()
    assert active["total"] == 1


def test_goal_user_scoped(client, user_token):
    from tests.conftest import register_and_login

    other_token = register_and_login(client, "othergoal@example.com", "othergoal")
    goal = client.post("/goals", headers=auth(user_token), json=GOAL).json()
    assert client.delete(f"/goals/{goal['id']}", headers=auth(other_token)).status_code == 404