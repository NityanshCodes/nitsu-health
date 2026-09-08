"""In-memory rate limiting.

A per-client-key sliding-window limiter used to protect sensitive endpoints
(e.g. login, registration, AI chat). In-memory is sufficient for a modular
monolith behind a single process; swap for a shared store (e.g. Redis) if
scaled to multiple workers.
"""

import threading
import time
from typing import Optional

from fastapi import HTTPException, Request, status

from app.core.config import settings


class RateLimiter:
    def __init__(self, window_seconds: int, max_requests: int):
        self.window_seconds = window_seconds
        self.max_requests = max_requests
        self._hits: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def _client_key(self, request: Request) -> str:
        # The request client host is used as the key. Behind a reverse proxy,
        # configure an appropriate forwarded-header-based key instead.
        return request.client.host if request.client else "unknown"

    def check(self, request: Request) -> None:
        if not settings.rate_limit_enabled:
            return
        key = self._client_key(request)
        now = time.monotonic()
        with self._lock:
            window = [t for t in self._hits.get(key, []) if now - t < self.window_seconds]
            if len(window) >= self.max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again later.",
                )
            window.append(now)
            self._hits[key] = window


class RateLimitDependency:
    """FastAPI dependency factory for per-endpoint rate limits."""

    def __init__(self, window_seconds: Optional[int] = None, max_requests: Optional[int] = None):
        self._limiter = RateLimiter(
            window_seconds=window_seconds or settings.rate_limit_window_seconds,
            max_requests=max_requests or settings.rate_limit_max_requests,
        )

    def __call__(self, request: Request) -> None:
        self._limiter.check(request)