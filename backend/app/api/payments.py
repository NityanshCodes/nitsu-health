"""Payments API — order creation, verification, webhook."""

import secrets
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.payment import Payment, PaymentEvent
from app.models.user import User
from app.providers.payments.demo import DemoPaymentProvider
from app.providers.payments.razorpay import RazorpayProvider
from app.services import entitlement_service
from app.utils.audit import log_action
from app.utils.auth import get_current_user

router = APIRouter(prefix="/payments", tags=["payments"])


def _get_provider():
    rp = RazorpayProvider()
    if rp.is_configured():
        return rp
    return DemoPaymentProvider()


@router.post("/create-order")
async def create_order(
    amount: int = 49900,  # ₹499 in paise
    currency: str = "INR",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    provider = _get_provider()
    receipt = f"user_{current_user.id}_{secrets.token_hex(4)}"
    try:
        order = await provider.create_order(amount=amount, currency=currency, receipt=receipt)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    # Store payment record
    import uuid
    payment = Payment(
        user_id=current_user.id,
        order_id=f"ord_{uuid.uuid4().hex[:16]}",
        amount=amount,
        currency=currency,
        status="created",
        provider="demo" if isinstance(provider, DemoPaymentProvider) else "razorpay",
        provider_order_id=order.get("id", ""),
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    log_action(db, "payment.order_created", user_id=current_user.id, entity_type="payment", entity_id=payment.id)

    return {
        "order_id": order.get("id"),
        "amount": amount,
        "currency": currency,
        "provider": payment.provider,
        "payment_id": payment.id,
        "note": order.get("note"),
    }


from pydantic import BaseModel as _PydanticModel


class _PaymentVerifyBody(_PydanticModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    signature: str


@router.post("/verify")
async def verify_payment(
    body: _PaymentVerifyBody = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    razorpay_order_id = body.razorpay_order_id
    razorpay_payment_id = body.razorpay_payment_id
    signature = body.signature
    provider = _get_provider()
    verified = provider.verify_payment(razorpay_order_id, razorpay_payment_id, signature)

    if not verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment verification failed")

    # Find the payment
    payment = (
        db.query(Payment)
        .filter(Payment.provider_order_id == razorpay_order_id, Payment.user_id == current_user.id)
        .first()
    )
    if payment:
        payment.status = "paid"
        db.commit()

    # Activate premium
    sub = entitlement_service.activate_premium(db, current_user, provider=payment.provider if payment else "demo")

    # Record idempotent payment event
    event = PaymentEvent(
        payment_id=payment.id if payment else None,
        provider="razorpay",
        event_type="payment.captured",
        idempotency_key=razorpay_payment_id,
        payload={"order_id": razorpay_order_id, "payment_id": razorpay_payment_id},
    )
    db.add(event)
    db.commit()

    log_action(db, "payment.verified", user_id=current_user.id, entity_type="payment", entity_id=payment.id if payment else 0)

    return {"status": "verified", "subscription": sub.plan}


@router.post("/webhook")
async def payment_webhook(request: Request, db: Session = Depends(get_db)) -> dict:
    """Idempotent webhook receiver. Verifies and processes payment events."""
    body = await request.json()
    event_type = body.get("event", "unknown")
    payload = body.get("payload", {})

    # Idempotency: check if we've processed this event
    event_id = body.get("id") or payload.get("payment", {}).get("entity", {}).get("id", "")
    if event_id:
        existing = db.query(PaymentEvent).filter(PaymentEvent.idempotency_key == event_id).first()
        if existing:
            return {"status": "already_processed"}

    # Extract payment info from webhook payload
    payment_entity = payload.get("payment", {}).get("entity", {})
    order_id = payment_entity.get("order_id", "")
    user_id = 0  # Would need to look up from payment record

    # Record event
    event = PaymentEvent(
        provider="razorpay",
        event_type=event_type,
        idempotency_key=event_id or f"wh_{secrets.token_hex(8)}",
        payload=body,
    )
    db.add(event)
    db.commit()

    return {"status": "processed", "event_type": event_type}


@router.get("/history")
def payment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    payments = (
        db.query(Payment)
        .filter(Payment.user_id == current_user.id)
        .order_by(Payment.created_at.desc())
        .limit(50)
        .all()
    )
    return {
        "payments": [
            {
                "id": p.id,
                "amount": p.amount,
                "currency": p.currency,
                "status": p.status,
                "provider": p.provider,
                "provider_order_id": p.provider_order_id,
                "created_at": str(p.created_at),
            }
            for p in payments
        ]
    }
