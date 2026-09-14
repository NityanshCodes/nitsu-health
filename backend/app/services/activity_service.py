"""Activity entry business logic."""

from datetime import datetime, time, timedelta
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.activity import ActivityEntry
from app.models.user import User


def _day_bounds(day: datetime) -> tuple[datetime, datetime]:
    start = datetime.combine(day.date(), time.min)
    end = datetime.combine(day.date(), time.max)
    return start, end


def list_entries(
    db: Session,
    user: User,
    day: Optional[datetime] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[ActivityEntry], int]:
    query = db.query(ActivityEntry).filter(ActivityEntry.user_id == user.id)
    if day:
        start, end = _day_bounds(day)
        query = query.filter(ActivityEntry.recorded_at >= start, ActivityEntry.recorded_at <= end)
    total = query.count()
    items = (
        query.order_by(ActivityEntry.recorded_at.desc(), ActivityEntry.id.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return items, total


def get_entry(db: Session, user: User, entry_id: int) -> Optional[ActivityEntry]:
    return (
        db.query(ActivityEntry)
        .filter(ActivityEntry.id == entry_id, ActivityEntry.user_id == user.id)
        .first()
    )


def create_entry(db: Session, user: User, data) -> ActivityEntry:
    entry = ActivityEntry(
        user_id=user.id,
        activity_type=data.activity_type,
        steps=data.steps,
        active_minutes=data.active_minutes,
        distance_km=data.distance_km,
        calories_burned=data.calories_burned,
        source=data.source,
        recorded_at=data.recorded_at or datetime.utcnow(),
        notes=data.notes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def update_entry(db: Session, user: User, entry_id: int, data) -> Optional[ActivityEntry]:
    entry = get_entry(db, user, entry_id)
    if entry is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(entry, field, value)
    db.commit()
    db.refresh(entry)
    return entry


def delete_entry(db: Session, user: User, entry_id: int) -> bool:
    entry = get_entry(db, user, entry_id)
    if entry is None:
        return False
    db.delete(entry)
    db.commit()
    return True


def daily_summary(db: Session, user: User, day: Optional[datetime] = None) -> dict:
    day = day or datetime.utcnow()
    start, end = _day_bounds(day)
    entries = (
        db.query(ActivityEntry)
        .filter(ActivityEntry.user_id == user.id, ActivityEntry.recorded_at >= start, ActivityEntry.recorded_at <= end)
        .all()
    )
    return {
        "user_id": user.id,
        "date": day.date(),
        "entries": len(entries),
        "total_steps": sum(e.steps or 0 for e in entries),
        "total_active_minutes": sum(e.active_minutes or 0 for e in entries),
        "total_distance_km": round(sum(e.distance_km or 0 for e in entries), 2),
        "total_calories_burned": round(sum(e.calories_burned or 0 for e in entries), 1),
        "activity_types": list({e.activity_type for e in entries}),
    }


def weekly_summary(db: Session, user: User, end_date: Optional[datetime] = None) -> dict:
    end_date = end_date or datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    entries = (
        db.query(ActivityEntry)
        .filter(ActivityEntry.user_id == user.id, ActivityEntry.recorded_at >= start_date, ActivityEntry.recorded_at <= end_date)
        .all()
    )
    return {
        "user_id": user.id,
        "period": f"{start_date.date()} to {end_date.date()}",
        "entries": len(entries),
        "total_steps": sum(e.steps or 0 for e in entries),
        "total_active_minutes": sum(e.active_minutes or 0 for e in entries),
        "total_distance_km": round(sum(e.distance_km or 0 for e in entries), 2),
        "total_calories_burned": round(sum(e.calories_burned or 0 for e in entries), 1),
    }
