import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(BASE_DIR / ".env")


def _split_csv(value: Optional[str], default: str) -> list[str]:
    if not value:
        return default.split(",")
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    app_name: str = "NITSU Health API"
    version: str = "0.1.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./nitsu_health.db")
    secret_key: str = os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY") or "dev-secret-key-change-me"
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY") or None
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ai_provider: str = os.getenv("AI_PROVIDER", "development")
    allowed_origins: list[str] = _split_csv(os.getenv("CORS_ORIGINS"), "http://localhost:5173,http://localhost:4173")
    allowed_origin_wildcard: bool = False


settings = Settings()
