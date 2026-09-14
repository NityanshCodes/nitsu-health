import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_email(value: str) -> str:
    """Basic email format check (stdlib-only; avoids a pydantic[email] hard dependency)."""
    if not _EMAIL_RE.match(value):
        raise ValueError("Invalid email format")
    return value


class RegisterRequest(BaseModel):
    email: str = Field(max_length=255)
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @field_validator("email")
    @classmethod
    def _check_email(cls, v: str) -> str:
        return _validate_email(v)


class LoginRequest(BaseModel):
    email: str = Field(max_length=255)
    password: str

    @field_validator("email")
    @classmethod
    def _check_email(cls, v: str) -> str:
        return _validate_email(v)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    onboarding_completed: bool = False


class UpdateProfileRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = Field(default=None, max_length=50)
    onboarding_completed: Optional[bool] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)
