"""AI insights + unified search tests."""

from tests.conftest import auth


def test_generate_and_list_insights(client, user_token):
    client.post(
        "/health/metrics",
        headers=auth(user_token),
        json={"metric_type": "weight", "value": 72, "unit": "kg"},
    )
    client.post(
        "/health/metrics",
        headers=auth(user_token),
        json={"metric_type": "weight", "value": 70, "unit": "kg"},
    )

    gen = client.post("/ai/insights/generate", headers=auth(user_token))
    assert gen.status_code == 200
    assert gen.json()["generated"] >= 1

    insights = client.get("/ai/insights", headers=auth(user_token)).json()
    assert insights["total"] >= 1
    first = insights["items"][0]
    assert first["title"]
    assert first["body"]
    assert "confidence" in first


def test_mark_insight_read(client, user_token):
    client.post("/health/metrics", headers=auth(user_token), json={"metric_type": "weight", "value": 72, "unit": "kg"})
    client.post("/health/metrics", headers=auth(user_token), json={"metric_type": "weight", "value": 70, "unit": "kg"})
    gen = client.post("/ai/insights/generate", headers=auth(user_token)).json()
    assert gen["generated"] >= 1
    insight_id = gen["insights"][0]["id"]

    marked = client.post(f"/ai/insights/{insight_id}/read", headers=auth(user_token))
    assert marked.json()["is_read"] is True


def test_insight_user_scoped(client, user_token):
    from tests.conftest import register_and_login

    other_token = register_and_login(client, "otherinsight@example.com", "otherinsight")
    client.post("/health/metrics", headers=auth(user_token), json={"metric_type": "weight", "value": 72, "unit": "kg"})
    client.post("/health/metrics", headers=auth(user_token), json={"metric_type": "weight", "value": 70, "unit": "kg"})
    gen = client.post("/ai/insights/generate", headers=auth(user_token)).json()
    insight_id = gen["insights"][0]["id"]
    assert client.post(f"/ai/insights/{insight_id}/read", headers=auth(other_token)).status_code == 404


def test_search_finds_user_data(client, user_token):
    client.post(
        "/nutrition",
        headers=auth(user_token),
        json={"meal_type": "dinner", "calories": 500, "protein_g": 30, "carbs_g": 50, "fats_g": 15, "water_ml": 400, "notes": "chicken bowl"},
    )
    results = client.get("/search?q=chicken", headers=auth(user_token)).json()
    assert results["total"] >= 1
    assert results["results"][0]["type"] == "nutrition"


def test_search_requires_two_chars(client, user_token):
    assert client.get("/search?q=a", headers=auth(user_token)).status_code == 422