"""Subscription state (FREE / PREMIUM)."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import PlanTier, SubscriptionStatus


class Subscription(Base):
    """A user's subscription to a plan tier.

    Payment providers are kept abstract; provider-specific identifiers are
    stored here but the entitlement system keys off `plan`/`status`.
    """

    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True, index=True)
    plan: Mapped[str] = mapped_column(String(20), default=PlanTier.FREE.value, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=SubscriptionStatus.INACTIVE.value, nullable=False)
    provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    provider_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="subscription")
