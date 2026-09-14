"""Reports generation + listing tests."""

from tests.conftest import auth


def test_generate_report_and_list(client, user_token):
    # Seed some data so the report has content.
    client.post(
        "/health/metrics",
        headers=auth(user_token),
        json={"metric_type": "weight", "value": 72, "unit": "kg"},
    )
    client.post(
        "/nutrition",
        headers=auth(user_token),
        json={"meal_type": "lunch", "calories": 600, "protein_g": 25, "carbs_g": 70, "fats_g": 18, "water_ml": 500},
    )

    gen = client.post("/reports/generate", headers=auth(user_token))
    assert gen.status_code == 201
    assert gen.json()["status"] == "generated"
    rid = gen.json()["id"]

    listed = client.get("/reports", headers=auth(user_token)).json()
    assert listed["total"] == 1

    detail = client.get(f"/reports/{rid}", headers=auth(user_token))
    assert detail.status_code == 200
    assert "report_data" in detail.json()
    assert "nutrition" in detail.json()["report_data"]


def test_latest_report_empty_state(client, user_token):
    latest = client.get("/reports/latest", headers=auth(user_token)).json()
    assert latest["status"] == "none"


def test_report_user_scoped(client, user_token):
    from tests.conftest import register_and_login

    other_token = register_and_login(client, "otherreport@example.com", "otherreport")
    rep = client.post("/reports/generate", headers=auth(user_token)).json()
    assert client.get(f"/reports/{rep['id']}", headers=auth(other_token)).status_code == 404