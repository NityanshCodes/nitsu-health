"""Application configuration, loaded from environment variables."""

import os
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent

try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")
    load_dotenv(BASE_DIR / ".env")
except ImportError:  # pragma: no cover - python-dotenv is optional for constrained environments
    def _load_dotenv_noop(*_args, **_kwargs):
        """No-op fallback so the app still imports without python-dotenv."""
        return False

    load_dotenv = _load_dotenv_noop


def _split_csv(value: Optional[str], default: str) -> list[str]:
    if not value:
        return default.split(",")
    return [item.strip() for item in value.split(",") if item.strip()]


def _env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, "true" if default else "false").lower() in {"1", "true", "yes", "on"}


class Settings:
    app_name: str = "NITSU Health API"
    version: str = "0.1.0"

    # Core
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = _env_bool("DEBUG", False)
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./nitsu_health.db")

    # Auth
    secret_key: str = os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY") or "dev-secret-key-change-me"
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # CORS
    allowed_origins: list[str] = _split_csv(
        os.getenv("CORS_ORIGINS"),
        "http://localhost:5173,http://localhost:4173",
    )
    allowed_origin_wildcard: bool = False

    # AI
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY") or None
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ai_provider: str = os.getenv("AI_PROVIDER", "development")

    # Wearables — OAuth secrets are backend-only (never sent to the frontend).
    fitbit_client_id: Optional[str] = os.getenv("FITBIT_CLIENT_ID") or None
    fitbit_client_secret: Optional[str] = os.getenv("FITBIT_CLIENT_SECRET") or None
    fitbit_redirect_uri: str = os.getenv("FITBIT_REDIRECT_URI", "http://localhost:8000/wearables/fitbit/callback")

    # Payments — secrets are backend-only.
    razorpay_key_id: Optional[str] = os.getenv("RAZORPAY_KEY_ID") or None
    razorpay_key_secret: Optional[str] = os.getenv("RAZORPAY_KEY_SECRET") or None
    razorpay_webhook_secret: Optional[str] = os.getenv("RAZORPAY_WEBHOOK_SECRET") or None
    # Default paid plan price (paise if using Razorpay currency minor units context).
    premium_price: float = float(os.getenv("PREMIUM_PRICE", "499"))
    payment_currency: str = os.getenv("PAYMENT_CURRENCY", "INR")
    frontend_base_url: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")

    # Security
    token_encryption_key: Optional[str] = os.getenv("TOKEN_ENCRYPTION_KEY") or None

    # Rate limiting (per-window per-client)
    rate_limit_enabled: bool = _env_bool("RATE_LIMIT_ENABLED", True)
    rate_limit_window_seconds: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    rate_limit_max_requests: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "60"))

    # Feature entitlements (configurable per tier)
    free_report_limit: int = int(os.getenv("FREE_REPORT_LIMIT", "2"))
    free_insight_limit: int = int(os.getenv("FREE_INSIGHT_LIMIT", "3"))
    free_ai_questions_per_day: int = int(os.getenv("FREE_AI_QUESTIONS_PER_DAY", "10"))


settings = Settings()