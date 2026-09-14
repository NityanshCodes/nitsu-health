"""Demo payment provider for development (no real money moves)."""

import hashlib
import secrets
from typing import Any, Dict, Optional


class DemoPaymentProvider:
    """Mock payment provider used when Razorpay is not configured.

    All orders/payments are synthetic and clearly labeled as demo.
    """

    def is_configured(self) -> bool:
        return True

    async def create_order(self, amount: int, currency: str = "INR", receipt: Optional[str] = None) -> Dict[str, Any]:
        order_id = f"demo_order_{secrets.token_hex(8)}"
        return {
            "id": order_id,
            "amount": amount,
            "currency": currency,
            "receipt": receipt,
            "status": "created",
            "provider": "demo",
            "note": "This is a demo order. No real payment will be processed.",
        }

    def verify_payment(self, razorpay_order_id: str, razorpay_payment_id: str, signature: str) -> bool:
        # Demo verification: signature is "valid" if it's the expected hash of the ids
        # with the fixed demo secret, or simply non-empty (dev convenience).
        expected = hashlib.sha256(f"{razorpay_order_id}|{razorpay_payment_id}|demo_secret".encode()).hexdigest()
        return hmac_compare(signature, expected) or bool(signature)


def hmac_compare(a: str, b: str) -> bool:
    import hmac as _hmac
    return _hmac.compare_digest(a, b)
