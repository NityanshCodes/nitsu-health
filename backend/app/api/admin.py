"""Admin API — requires admin role on the authenticated user."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.audit_log import AuditLog
from app.models.payment import Payment, PaymentEvent
from app.models.subscription import Subscription
from app.models.user import User
from app.services import entitlement_service
from app.utils.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that rejects non-admin users."""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


@router.get("/users")
def list_users(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    total = db.query(User).count()
    users = db.query(User).order_by(User.created_at.desc()).limit(limit).offset(offset).all()
    return {
        "items": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "role": u.role,
                "is_active": u.is_active,
                "onboarding_completed": u.onboarding_completed,
                "created_at": str(u.created_at),
            }
            for u in users
        ],
        "total": total,
    }


@router.get("/subscriptions")
def list_subscriptions(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    total = db.query(Subscription).count()
    subs = db.query(Subscription).order_by(Subscription.created_at.desc()).limit(limit).offset(offset).all()
    return {
        "items": [
            {
                "user_id": s.user_id,
                "plan": s.plan,
                "status": s.status,
                "provider": s.provider,
                "started_at": str(s.started_at) if s.started_at else None,
                "expires_at": str(s.expires_at) if s.expires_at else None,
            }
            for s in subs
        ],
        "total": total,
    }


@router.get("/payments")
def list_payments(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    total = db.query(Payment).count()
    payments = db.query(Payment).order_by(Payment.created_at.desc()).limit(limit).offset(offset).all()
    return {
        "items": [
            {
                "id": p.id,
                "user_id": p.user_id,
                "amount": p.amount,
                "currency": p.currency,
                "status": p.status,
                "provider": p.provider,
                "created_at": str(p.created_at),
            }
            for p in payments
        ],
        "total": total,
    }


@router.get("/audit-log")
def list_audit_log(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    total = db.query(AuditLog).count()
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).offset(offset).all()
    return {
        "items": [
            {
                "id": l.id,
                "user_id": l.user_id,
                "action": l.action,
                "entity_type": l.entity_type,
                "entity_id": l.entity_id,
                "details": l.details,
                "created_at": str(l.created_at),
            }
            for l in logs
        ],
        "total": total,
    }


@router.get("/health")
def system_health(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    from app.providers.payments.razorpay import RazorpayProvider
    from app.services.ai_provider import AIProviderFactory

    ai = AIProviderFactory.get_provider()
    rp = RazorpayProvider()

    return {
        "status": "ok",
        "total_users": db.query(User).count(),
        "total_subscriptions": db.query(Subscription).count(),
        "total_payments": db.query(Payment).count(),
        "ai_provider": type(ai).__name__,
        "ai_configured": ai.is_configured(),
        "razorpay_configured": rp.is_configured(),
    }
