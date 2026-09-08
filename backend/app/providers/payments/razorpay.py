"""Razorpay payment provider.

REQUIRES USER CONFIGURATION: Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET
environment variables with your Razorpay credentials.
"""

import hashlib
import hmac
import os
from typing import Any, Dict, Optional

try:  # httpx is only needed for real Razorpay API calls
    import httpx
except ImportError:  # pragma: no cover - optional dependency for constrained environments
    httpx = None  # type: ignore


class RazorpayProvider:
    """Real Razorpay integration."""

    BASE_URL = "https://api.razorpay.com/v1"

    def __init__(self):
        self.key_id = os.getenv("RAZORPAY_KEY_ID")
        self.key_secret = os.getenv("RAZORPAY_KEY_SECRET")

    def is_configured(self) -> bool:
        return bool(self.key_id and self.key_secret and httpx is not None)

    async def create_order(self, amount: int, currency: str = "INR", receipt: Optional[str] = None) -> Dict[str, Any]:
        if not self.is_configured():
            raise ValueError("Razorpay is not configured")
        if httpx is None:
            raise ValueError("httpx is not installed; it is required for the Razorpay provider")
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/orders",
                json={"amount": amount, "currency": currency, "receipt": receipt},
                auth=(self.key_id, self.key_secret),
            )
            resp.raise_for_status()
            return resp.json()

    def verify_payment(self, razorpay_order_id: str, razorpay_payment_id: str, signature: str) -> bool:
        if not self.is_configured():
            return False
        expected = hmac.new(
            self.key_secret.encode(),
            f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
