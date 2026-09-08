"""Health profile — user-provided health context, separated from account data."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class HealthProfile(Base):
    """User-supplied health information.

    Kept logically separate from account/authentication data (the User
    model). Family history lives in its own model so this stays focused on
    the individual's own profile.
    """

    __tablename__ = "health_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True, index=True)
    height_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    blood_type: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    medical_conditions: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    allergies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    medications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lifestyle: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # activity, diet, sleep habits
    health_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="health_profile")
