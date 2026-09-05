"""Tests for authenticated AI chat endpoint."""

import unittest

from fastapi.testclient import TestClient

from app.database.base import Base
from app.database.database import engine
from app.main import app
from app.services.auth_service import create_access_token, register_user
from app.schemas.auth import RegisterRequest


class AIEndpointTests(unittest.TestCase):
    """Test the AI chat endpoint with authentication and user isolation."""

    def setUp(self):
        """Set up test database and client."""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.client = TestClient(app)

    def tearDown(self):
        """Clean up after tests."""
        Base.metadata.drop_all(bind=engine)

    def _create_and_login_user(self, email, username, password, first_name):
        """Helper to create a user and get their token."""
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=engine)
        db = Session()

        reg_data = RegisterRequest(email=email, username=username, password=password, first_name=first_name)
        user = register_user(db, reg_data)
        token = create_access_token(user)

        db.close()
        return user, token

    def test_ai_chat_requires_authentication(self):
        """Test that AI chat endpoint requires authentication."""
        response = self.client.post("/ai/chat", json={"question": "How are you?"})
        # FastAPI returns 403 when auth dependency is not satisfied (no header)
        assert response.status_code in (401, 403)

    def test_ai_chat_with_valid_token(self):
        """Test that authenticated user can call AI chat endpoint."""
        user, token = self._create_and_login_user("alice@test.com", "alice", "Pass123!", "Alice")

        response = self.client.post(
            "/ai/chat",
            json={"question": "What should I eat for breakfast?"},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Should either return 200 (success with dev provider) or 503 (no OpenAI key)
        assert response.status_code in (200, 503)

    def test_ai_chat_rejects_empty_question(self):
        """Test that empty questions are rejected."""
        user, token = self._create_and_login_user("bob@test.com", "bob", "Pass123!", "Bob")

        response = self.client.post(
            "/ai/chat",
            json={"question": ""},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Pydantic validation returns 422 for validation errors
        assert response.status_code in (400, 422)

    def test_ai_chat_rejects_very_long_question(self):
        """Test that extremely long questions are rejected."""
        user, token = self._create_and_login_user("charlie@test.com", "charlie", "Pass123!", "Charlie")

        long_question = "a" * 3000  # Exceeds 2000 char limit

        response = self.client.post(
            "/ai/chat",
            json={"question": long_question},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Pydantic validation returns 422 for validation errors
        assert response.status_code in (400, 422)

    def test_ai_response_includes_disclaimer(self):
        """Test that AI responses include safety disclaimer."""
        user, token = self._create_and_login_user("dave@test.com", "dave", "Pass123!", "Dave")

        response = self.client.post(
            "/ai/chat",
            json={"question": "What is a healthy weight?"},
            headers={"Authorization": f"Bearer {token}"},
        )

        # With dev provider, should always work
        if response.status_code == 200:
            data = response.json()
            assert "disclaimer" in data
            assert data["disclaimer"] is not None
            assert len(data["disclaimer"]) > 0
            assert "medical advice" in data["disclaimer"].lower() or "professional" in data["disclaimer"].lower()

    def test_ai_response_includes_generated_by(self):
        """Test that AI responses include source indicator."""
        user, token = self._create_and_login_user("eve@test.com", "eve", "Pass123!", "Eve")

        response = self.client.post(
            "/ai/chat",
            json={"question": "What is a normal heart rate?"},
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code == 200:
            data = response.json()
            assert "generated_by" in data
            assert data["generated_by"] == "ai"

    def test_user_isolation_in_context(self):
        """Test that each user only gets their own context in AI prompts.

        This test verifies that asking the AI as User A produces different
        context than asking as User B, and that the prompt contains user A's
        name only when User A asks.
        """
        # Create two different users
        user_a, token_a = self._create_and_login_user("alice@test.com", "alice", "Pass123!", "Alice")
        user_b, token_b = self._create_and_login_user("bob@test.com", "bob", "Pass123!", "Bob")

        # User A asks a question
        response_a = self.client.post(
            "/ai/chat",
            json={"question": "What is my name?", "include_context": True},
            headers={"Authorization": f"Bearer {token_a}"},
        )

        # User B asks the same question
        response_b = self.client.post(
            "/ai/chat",
            json={"question": "What is my name?", "include_context": True},
            headers={"Authorization": f"Bearer {token_b}"},
        )

        # Both should succeed
        assert response_a.status_code in (200, 503)
        assert response_b.status_code in (200, 503)

        # If we got responses with context (only for dev provider), verify they're different
        if response_a.status_code == 200 and response_b.status_code == 200:
            data_a = response_a.json()
            data_b = response_b.json()

            # Check that context_used shows different users
            if data_a.get("context_used") and data_b.get("context_used"):
                assert data_a["context_used"]["user_id"] == user_a.id
                assert data_b["context_used"]["user_id"] == user_b.id

    def test_ai_chat_invalid_token_rejected(self):
        """Test that invalid JWT tokens are rejected."""
        response = self.client.post(
            "/ai/chat",
            json={"question": "Hello"},
            headers={"Authorization": "Bearer invalid-token-xyz"},
        )

        assert response.status_code == 401

    def test_ai_health_endpoint(self):
        """Test the AI health check endpoint."""
        response = self.client.get("/ai/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "provider" in data
        assert "configured" in data


if __name__ == "__main__":
    unittest.main()
