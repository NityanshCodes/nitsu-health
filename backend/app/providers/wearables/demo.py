"""Demo wearable provider for development (safe, clearly-labeled mock data)."""

from datetime import date, timedelta
from typing import Any, Dict


class DemoWearableProvider:
    """Mock wearable provider used when real credentials are not configured.

    All data is synthetic and clearly labeled as demo.
    """

    def is_configured(self) -> bool:
        return True

    def auth_url(self, state: str) -> str:
        return f"http://localhost:8000/api/v1/wearables/fitbit/callback?code=demo_code&state={state}"

    async def exchange_code(self, code: str) -> Dict[str, Any]:
        return {
            "access_token": "demo_access_token",
            "refresh_token": "demo_refresh_token",
            "expires_in": 28800,
            "scope": "activity heartrate sleep weight profile",
            "token_type": "Bearer",
        }

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        return {
            "access_token": "demo_access_token_refreshed",
            "refresh_token": "demo_refresh_token_new",
            "expires_in": 28800,
            "token_type": "Bearer",
        }

    async def fetch_metrics(self, access_token: str, period_days: int = 7) -> Dict[str, Any]:
        """Return clearly synthetic demo data."""
        end = date.today()
        days = []
        for i in range(period_days):
            d = end - timedelta(days=i)
            days.append({
                "date": str(d),
                "steps": 5000 + (i * 700) % 3000,
                "active_minutes": 30 + (i * 10) % 60,
                "distance_km": round(3.5 + (i * 0.5) % 2.0, 2),
                "calories_burned": 1800 + (i * 100) % 500,
                "sleep_minutes": 420 + (i * 30) % 90,
                "sleep_stages": {
                    "deep": 60 + (i * 5) % 30,
                    "light": 200 + (i * 10) % 60,
                    "rem": 90 + (i * 10) % 40,
                    "awake": 20 + (i * 5) % 15,
                },
            })
        return {
            "source": "demo",
            "note": "This is synthetic demo data for development. Not real health data.",
            "days": days,
        }
