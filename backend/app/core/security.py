import os
from typing import Any, Optional

from fastapi import HTTPException, status
from fastapi.security import HTTPBearer

bearer_scheme = HTTPBearer(auto_error=False)


def get_api_key() -> str:
    key = os.getenv("API_KEY", "dev-api-key")
    if not key:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="API_KEY not configured")
    return key


def validate_api_key(api_key: Optional[str]) -> bool:
    if not api_key:
        return False
    return api_key == get_api_key()


def require_api_key(api_key: Optional[str]) -> None:
    if not validate_api_key(api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
