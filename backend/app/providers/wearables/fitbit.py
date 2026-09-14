"""Fitbit OAuth2 wearable provider."""

import os
from typing import Any, Dict

try:  # httpx is only needed for real Fitbit API calls
    import httpx
except ImportError:  # pragma: no cover - optional dependency for constrained environments
    httpx = None  # type: ignore

from app.providers.wearables import WearableProvider


class FitbitProvider(WearableProvider):
    """Real Fitbit Web API integration.

    REQUIRES USER CONFIGURATION: Set FITBIT_CLIENT_ID and FITBIT_CLIENT_SECRET
    environment variables with your Fitbit developer app credentials.
    """

    BASE_URL = "https://api.fitbit.com"
    AUTH_URL = "https://www.fitbit.com/oauth2/authorize"
    TOKEN_URL = "https://api.fitbit.com/oauth2/token"

    def __init__(self):
        self.client_id = os.getenv("FITBIT_CLIENT_ID")
        self.client_secret = os.getenv("FITBIT_CLIENT_SECRET")
        self.redirect_uri = os.getenv("FITBIT_REDIRECT_URI", "http://localhost:8000/api/v1/wearables/fitbit/callback")

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret and httpx is not None)

    def _require_httpx(self) -> None:
        if httpx is None:
            raise ValueError("httpx is not installed; it is required for the Fitbit provider")

    def auth_url(self, state: str) -> str:
        scopes = "activity heartrate sleep weight profile"
        return (
            f"{self.AUTH_URL}"
            f"?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope={scopes}"
            f"&state={state}"
        )

    async def exchange_code(self, code: str) -> Dict[str, Any]:
        self._require_httpx()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                },
                auth=(self.client_id, self.client_secret),
            )
            resp.raise_for_status()
            return resp.json()

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        self._require_httpx()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
                auth=(self.client_id, self.client_secret),
            )
            resp.raise_for_status()
            return resp.json()

    async def fetch_metrics(self, access_token: str, period_days: int = 7) -> Dict[str, Any]:
        from datetime import date, timedelta

        end = date.today()
        start = end - timedelta(days=period_days - 1)
        headers = {"Authorization": f"Bearer {access_token}"}

        self._require_httpx()
        async with httpx.AsyncClient() as client:
            # Steps & activity
            act_resp = await client.get(
                f"{self.BASE_URL}/1/user/-/activities/date/{start}/{end}.json",
                headers=headers,
            )
            act_resp.raise_for_status()
            activity_data = act_resp.json()

            # Sleep
            sleep_resp = await client.get(
                f"{self.BASE_URL}/1.2/user/-/sleep/date/{start}/{end}.json",
                headers=headers,
            )
            sleep_resp.raise_for_status()
            sleep_data = sleep_resp.json()

        return {
            "period": f"{start} to {end}",
            "activity": activity_data,
            "sleep": sleep_data,
        }
