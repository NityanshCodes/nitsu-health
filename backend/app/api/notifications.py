"""Notifications API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.notification import NotificationResponse
from app.services import notification_service
from app.utils.auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
def list_notifications(
    unread_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    items, total = notification_service.list_notifications(db, current_user, unread_only, limit, offset)
    return {
        "items": [NotificationResponse.model_validate(n) for n in items],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationResponse:
    notif = notification_service.mark_read(db, current_user, notification_id)
    if notif is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return NotificationResponse.model_validate(notif)


@router.post("/read-all")
def mark_all_read(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    count = notification_service.mark_all_read(db, current_user)
    return {"marked_read": count}
