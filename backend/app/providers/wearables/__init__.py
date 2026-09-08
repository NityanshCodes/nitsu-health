"""Wearable provider abstraction."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class WearableProvider(ABC):
    """Base class for wearable data providers."""

    @abstractmethod
    def auth_url(self, state: str) -> str:
        """Return the OAuth authorization URL."""
        ...

    @abstractmethod
    async def exchange_code(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens."""
        ...

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh an expired access token."""
        ...

    @abstractmethod
    async def fetch_metrics(self, access_token: str, period_days: int = 7) -> Dict[str, Any]:
        """Fetch recent health metrics from the provider."""
        ...

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if credentials are available."""
        ...
