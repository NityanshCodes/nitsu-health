"""Shared pytest fixtures for NITSU Health backend tests."""

import os

# Must be set before importing app modules.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_main.db")
os.environ.setdefault("ENVIRONMENT", "test")

import pytest
from fastapi.testclient import TestClient

from app.database.base import Base
from app.database.database import engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestClient(app)


def register_and_login(client: TestClient, email: str, username: str, password: str = "StrongPass123!") -> str:
    """Register a user and return an access token."""
    client.post(
        "/auth/register",
        json={"email": email, "username": username, "password": password},
    )
    token = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    ).json()["access_token"]
    return token


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def user_token(client):
    return register_and_login(client, "test@example.com", "testuser")


@pytest.fixture()
def admin_token(client):
    client.post(
        "/auth/register",
        json={"email": "admin@example.com", "username": "admin", "password": "StrongPass123!"},
    )
    # Promote to admin directly in DB
    from sqlalchemy.orm import sessionmaker
    from app.models.user import User

    Session = sessionmaker(bind=engine)
    db = Session()
    admin_user = db.query(User).filter(User.username == "admin").first()
    admin_user.role = "admin"
    db.commit()
    db.close()

    token = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "StrongPass123!"},
    ).json()["access_token"]
    return token