import re
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.schemas.auth import ChangePasswordRequest, LoginRequest, RegisterRequest, UpdateProfileRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _validate_password(password: str) -> None:
    if len(password) < 8:
        raise ValueError("password must be at least 8 characters long")
    if not re.search(r"[A-Z]", password):
        raise ValueError("password must include at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValueError("password must include at least one lowercase letter")
    if not re.search(r"\d", password):
        raise ValueError("password must include at least one number")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise JWTError("invalid token") from exc


def register_user(db: Session, data: RegisterRequest) -> User:
    _validate_password(data.password)

    existing_user = db.query(User).filter((User.email == data.email) | (User.username == data.username)).first()
    if existing_user:
        if existing_user.email == data.email:
            raise ValueError("email already registered")
        raise ValueError("username already registered")

    user = User(
        email=data.email,
        username=data.username,
        password_hash=get_password_hash(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, data: LoginRequest) -> Optional[User]:
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        return None
    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def update_profile(db: Session, user: User, data: UpdateProfileRequest) -> User:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, data: ChangePasswordRequest) -> User:
    if not verify_password(data.current_password, user.password_hash):
        raise ValueError("current password is incorrect")
    _validate_password(data.new_password)
    user.password_hash = get_password_hash(data.new_password)
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user
