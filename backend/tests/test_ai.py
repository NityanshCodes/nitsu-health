"""AI chat, context, conversations, provider tests."""

from tests.conftest import auth


def test_ai_chat_development_provider(client, user_token):
    resp = client.post(
        "/ai/chat",
        headers=auth(user_token),
        json={"question": "Hello AI"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["answer"]
    assert data["generated_by"] == "ai"
    assert data["disclaimer"]


def test_ai_chat_context_includes_health_data(client, user_token):
    # Seed some data so AI context has real info
    client.post(
        "/health/metrics",
        headers=auth(user_token),
        json={"metric_type": "weight", "value": 72, "unit": "kg"},
    )

    resp = client.post(
        "/ai/chat",
        headers=auth(user_token),
        json={"question": "What is my weight?"},
    )
    assert resp.status_code == 200
    assert resp.json()["answer"]


def test_ai_conversations_list(client, user_token):
    # Create a conversation via chat
    client.post("/ai/chat", headers=auth(user_token), json={"question": "Hello"})

    # List conversations
    resp = client.get("/ai/conversations", headers=auth(user_token))
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1

    # Get specific conversation
    conv_id = resp.json()["items"][0]["id"]
    detail = client.get(f"/ai/conversations/{conv_id}", headers=auth(user_token))
    assert detail.status_code == 200
    assert len(detail.json()["messages"]) >= 1


def test_ai_conversation_user_scoped(client, user_token):
    from tests.conftest import register_and_login

    other_token = register_and_login(client, "otherai@example.com", "otherai")

    client.post("/ai/chat", headers=auth(user_token), json={"question": "Hello"})

    my_convs = client.get("/ai/conversations", headers=auth(user_token)).json()
    other_convs = client.get("/ai/conversations", headers=auth(other_token)).json()

    assert my_convs["total"] >= 1
    assert other_convs["total"] == 0

    # Accessing other user's conversation → 404
    conv_id = my_convs["items"][0]["id"]
    assert client.get(f"/ai/conversations/{conv_id}", headers=auth(other_token)).status_code == 404


def test_ai_chat_with_history(client, user_token):
    """Test multi-turn conversation via conversation_id query param."""
    resp1 = client.post(
        "/ai/chat",
        headers=auth(user_token),
        json={"question": "My name is Test"},
    )
    # Find the conversation created by the first turn
    convs = client.get("/ai/conversations", headers=auth(user_token)).json()
    conv_id = convs["items"][0]["id"]

    resp2 = client.post(
        f"/ai/chat?conversation_id={conv_id}",
        headers=auth(user_token),
        json={"question": "What is my name?"},
    )
    assert resp2.status_code == 200
    assert resp2.json()["answer"]


def test_ai_chat_empty_message_rejected(client, user_token):
    resp = client.post(
        "/ai/chat",
        headers=auth(user_token),
        json={"question": ""},
    )
    # min_length=1 in the schema → 422
    assert resp.status_code == 422


def test_ai_health_endpoint(client, user_token):
    resp = client.get("/ai/health", headers=auth(user_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "provider" in data
    assert "configured" in data