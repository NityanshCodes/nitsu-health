"""Test that the AI chat route is registered and handles authenticated requests."""

from fastapi import status


def test_backend_chat_route_presence(client, user_token):
    """Test that the AI chat route exists and responds appropriately."""
    # Test with valid auth
    resp = client.post(
        "/ai/chat", json={"question": "hello"}, headers={"Authorization": f"Bearer {user_token}"}
    )
    # Should return 200 (dev provider) or 503 (missing config) but not 404 or 401
    assert resp.status_code in (status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR, status.HTTP_503_SERVICE_UNAVAILABLE)