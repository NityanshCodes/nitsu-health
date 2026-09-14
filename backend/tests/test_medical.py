"""Medical records API tests."""

from tests.conftest import auth

RECORD = {
    "category": "report",
    "title": "Annual physical results",
    "description": "Summary of annual checkup",
}


def test_medical_record_crud(client, user_token):
    created = client.post("/medical-records", headers=auth(user_token), data=RECORD)
    assert created.status_code == 201
    rid = created.json()["id"]
    assert created.json()["category"] == "report"

    listed = client.get("/medical-records", headers=auth(user_token)).json()
    assert listed["total"] == 1
    assert listed["items"][0]["title"] == "Annual physical results"

    assert client.delete(f"/medical-records/{rid}", headers=auth(user_token)).status_code == 204
    assert client.get(f"/medical-records/{rid}", headers=auth(user_token)).status_code == 404


def test_medical_record_filter_by_category(client, user_token):
    client.post("/medical-records", headers=auth(user_token), data=RECORD)
    filtered = client.get("/medical-records?category=report", headers=auth(user_token)).json()
    assert filtered["total"] == 1
    none = client.get("/medical-records?category=imaging", headers=auth(user_token)).json()
    assert none["total"] == 0


def test_medical_record_user_scoped(client, user_token):
    from tests.conftest import register_and_login

    other_token = register_and_login(client, "othermed@example.com", "othermed")
    rec = client.post("/medical-records", headers=auth(user_token), data=RECORD).json()
    assert client.delete(f"/medical-records/{rec['id']}", headers=auth(other_token)).status_code == 404