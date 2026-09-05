import os
import unittest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_auth.db")

from fastapi.testclient import TestClient

from app.database.base import Base
from app.database.database import engine
from app.main import app


class AuthFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.client = TestClient(app)

    def test_register_login_and_profile_flow(self) -> None:
        register_response = self.client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "username": "user1",
                "password": "StrongPass123!",
                "first_name": "Ada",
                "last_name": "Lovelace",
            },
        )

        self.assertEqual(register_response.status_code, 201)
        self.assertEqual(register_response.json()["email"], "user@example.com")

        login_response = self.client.post(
            "/auth/login",
            json={"email": "user@example.com", "password": "StrongPass123!"},
        )

        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access_token", login_response.json())

        token = login_response.json()["access_token"]
        profile_response = self.client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(profile_response.status_code, 200)
        self.assertEqual(profile_response.json()["username"], "user1")

    def test_duplicate_email_is_rejected(self) -> None:
        self.client.post(
            "/auth/register",
            json={
                "email": "dup@example.com",
                "username": "dup1",
                "password": "StrongPass123!",
            },
        )

        duplicate_response = self.client.post(
            "/auth/register",
            json={
                "email": "dup@example.com",
                "username": "dup2",
                "password": "StrongPass123!",
            },
        )

        self.assertEqual(duplicate_response.status_code, 400)

    def test_invalid_token_is_rejected(self) -> None:
        response = self.client.get(
            "/users/me",
            headers={"Authorization": "Bearer invalid-token"},
        )

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
