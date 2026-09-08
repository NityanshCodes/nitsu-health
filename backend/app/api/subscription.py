"""Subscription API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.services import entitlement_service
from app.utils.auth import get_current_user

router = APIRouter(prefix="/subscription", tags=["subscription"])


@router.get("/status")
def subscription_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    sub = entitlement_service.get_subscription(db, current_user)
    return {
        "plan": sub.plan,
        "status": sub.status,
        "provider": sub.provider,
        "started_at": str(sub.started_at) if sub.started_at else None,
        "expires_at": str(sub.expires_at) if sub.expires_at else None,
    }


@router.get("/plan")
def subscription_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    plan = entitlement_service.get_plan(db, current_user)
    features = {f: entitlement_service.check(db, current_user, f) for f in entitlement_service.FEATURE_MAP}
    return {
        "plan": plan,
        "features": features,
    }


@router.post("/downgrade")
def downgrade_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    sub = entitlement_service.downgrade_to_free(db, current_user)
    return {"plan": sub.plan, "status": sub.status}
