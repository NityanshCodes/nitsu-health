"""Payment provider abstraction."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class PaymentProvider(ABC):
    """Base class for payment providers."""

    @abstractmethod
    async def create_order(self, amount: int, currency: str = "INR", receipt: Optional[str] = None) -> Dict[str, Any]:
        """Create a payment order. Amount in smallest currency unit (paise)."""
        ...

    @abstractmethod
    def verify_payment(self, razorpay_order_id: str, razorpay_payment_id: str, signature: str) -> bool:
        """Verify payment signature from provider callback."""
        ...

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if credentials are available."""
        ...
