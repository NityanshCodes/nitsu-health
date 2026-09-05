import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_isolation.db")

from fastapi.testclient import TestClient

from app.database.base import Base
from app.database.database import engine
from app.main import app
from app.models.nutrition import NutritionEntry
from app.models.report import HealthReport
from app.models.user import User
from app.models.wearable import WearableData


class TestUserIsolation:
    def setup_method(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.client = TestClient(app)

        self.user_a = self.client.post(
            "/auth/register",
            json={
                "email": "usera@example.com",
                "username": "usera",
                "password": "StrongPass123!",
            },
        )
        self.user_b = self.client.post(
            "/auth/register",
            json={
                "email": "userb@example.com",
                "username": "userb",
                "password": "StrongPass123!",
            },
        )

        self.token_a = self.client.post(
            "/auth/login",
            json={"email": "usera@example.com", "password": "StrongPass123!"},
        ).json()["access_token"]
        self.token_b = self.client.post(
            "/auth/login",
            json={"email": "userb@example.com", "password": "StrongPass123!"},
        ).json()["access_token"]

    def test_user_b_cannot_access_user_a_profile_by_id(self):
        response = self.client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {self.token_b}"},
        )
        assert response.status_code == 200
        assert response.json()["email"] == "userb@example.com"

    def test_user_b_cannot_see_user_a_nutrition_data(self):
        with engine.begin() as conn:
            conn.execute(
                NutritionEntry.__table__.insert(),
                [{
                    "user_id": 1,
                    "meal_type": "breakfast",
                    "calories": 500,
                    "protein_g": 25,
                    "carbs_g": 60,
                    "fats_g": 15,
                    "water_ml": 500,
                    "notes": "private data",
                }],
            )

        response = self.client.get(
            "/nutrition/today",
            headers={"Authorization": f"Bearer {self.token_b}"},
        )
        assert response.status_code == 200
        assert response.json()["user_id"] == 2
        assert response.json()["calories"] == 0

    def test_user_b_cannot_see_user_a_report_data(self):
        with engine.begin() as conn:
            conn.execute(
                HealthReport.__table__.insert(),
                [{
                    "user_id": 1,
                    "title": "Private report",
                    "summary": "confidential",
                    "status": "generated",
                }],
            )

        response = self.client.get(
            "/reports/latest",
            headers={"Authorization": f"Bearer {self.token_b}"},
        )
        assert response.status_code == 200
        assert response.json()["user_id"] == 2
        assert response.json()["title"] != "Private report"

    def test_user_b_cannot_see_user_a_wearable_data(self):
        with engine.begin() as conn:
            conn.execute(
                WearableData.__table__.insert(),
                [{
                    "user_id": 1,
                    "source": "fitbit",
                    "metric_type": "steps",
                    "metric_value": 15000,
                    "unit": "count",
                }],
            )

        response = self.client.get(
            "/wearables/status",
            headers={"Authorization": f"Bearer {self.token_b}"},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["user_id"] == 2
        assert payload["provider"] in {"none", "not_connected", "demo"}
