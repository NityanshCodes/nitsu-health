"""Notification business logic."""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User


def list_notifications(
    db: Session,
    user: User,
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Notification], int]:
    query = db.query(Notification).filter(Notification.user_id == user.id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    total = query.count()
    items = query.order_by(Notification.created_at.desc()).limit(limit).offset(offset).all()
    return items, total


def mark_read(db: Session, user: User, notification_id: int) -> Optional[Notification]:
    notif = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == user.id)
        .first()
    )
    if notif is None:
        return None
    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif


def mark_all_read(db: Session, user: User) -> int:
    count = (
        db.query(Notification)
        .filter(Notification.user_id == user.id, Notification.is_read == False)
        .update({"is_read": True})
    )
    db.commit()
    return count


def create_notification(
    db: Session,
    user_id: int,
    type_: str,
    title: str,
    body: Optional[str] = None,
) -> Notification:
    notif = Notification(
        user_id=user_id,
        type=type_,
        title=title,
        body=body,
        is_read=False,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif
