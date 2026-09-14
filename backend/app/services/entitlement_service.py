"""Entitlement service — central FREE vs PREMIUM feature gate."""

from app.core.config import settings
from app.models.subscription import Subscription
from app.models.user import User
from sqlalchemy.orm import Session


# Feature map: feature name → minimum plan required
# Configurable limits live in settings; this map is the single source of truth
# for which features are gated.
FEATURE_MAP = {
    "ai_chat": "FREE",
    "basic_analytics": "FREE",
    "manual_data_entry": "FREE",
    "ai_insights": "PREMIUM",
    "ai_reports": "PREMIUM",
    "advanced_analytics": "PREMIUM",
    "wearable_sync": "PREMIUM",
    "unlimited_goals": "PREMIUM",
}

PLAN_RANK = {"FREE": 0, "PREMIUM": 1}


def get_subscription(db: Session, user: User) -> Subscription:
    """Get or create the user's subscription record."""
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if sub is None:
        sub = Subscription(
            user_id=user.id,
            plan="FREE",
            status="active",
            provider="none",
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
    return sub


def get_plan(db: Session, user: User) -> str:
    """Return the user's current effective plan."""
    sub = get_subscription(db, user)
    if sub.status != "active":
        return "FREE"
    # Check expiry
    if sub.expires_at and sub.expires_at < __import__("datetime").datetime.utcnow():
        return "FREE"
    return sub.plan


def check(db: Session, user: User, feature: str) -> bool:
    """Check whether a user has access to a feature."""
    required = FEATURE_MAP.get(feature)
    if required is None:
        # Unknown features are not gated
        return True
    user_plan = get_plan(db, user)
    return PLAN_RANK.get(user_plan, 0) >= PLAN_RANK.get(required, 0)


def activate_premium(db: Session, user: User, provider: str = "demo", provider_subscription_id: str | None = None) -> Subscription:
    """Activate a PREMIUM subscription (called after successful payment)."""
    from datetime import datetime, timedelta
    sub = get_subscription(db, user)
    sub.plan = "PREMIUM"
    sub.status = "active"
    sub.provider = provider
    sub.provider_subscription_id = provider_subscription_id
    sub.started_at = datetime.utcnow()
    sub.expires_at = datetime.utcnow() + timedelta(days=30)
    db.commit()
    db.refresh(sub)
    return sub


def downgrade_to_free(db: Session, user: User) -> Subscription:
    sub = get_subscription(db, user)
    sub.plan = "FREE"
    sub.provider = "none"
    sub.provider_subscription_id = None
    sub.expires_at = None
    db.commit()
    db.refresh(sub)
    return sub
