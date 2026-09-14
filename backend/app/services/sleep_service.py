"""Sleep entry business logic."""

from datetime import datetime, time, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.sleep import SleepEntry
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
) -> tuple[list[SleepEntry], int]:
    query = db.query(SleepEntry).filter(SleepEntry.user_id == user.id)
    if day:
        start, end = _day_bounds(day)
        query = query.filter(SleepEntry.start_time >= start, SleepEntry.start_time <= end)
    total = query.count()
    items = (
        query.order_by(SleepEntry.start_time.desc(), SleepEntry.id.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return items, total


def get_entry(db: Session, user: User, entry_id: int) -> Optional[SleepEntry]:
    return (
        db.query(SleepEntry)
        .filter(SleepEntry.id == entry_id, SleepEntry.user_id == user.id)
        .first()
    )


def create_entry(db: Session, user: User, data) -> SleepEntry:
    entry = SleepEntry(
        user_id=user.id,
        start_time=data.start_time,
        end_time=data.end_time,
        duration_minutes=data.duration_minutes,
        sleep_stages=data.sleep_stages,
        source=data.source,
        notes=data.notes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def update_entry(db: Session, user: User, entry_id: int, data) -> Optional[SleepEntry]:
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


def weekly_average(db: Session, user: User, end_date: Optional[datetime] = None) -> dict:
    end_date = end_date or datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    entries = (
        db.query(SleepEntry)
        .filter(SleepEntry.user_id == user.id, SleepEntry.start_time >= start_date, SleepEntry.start_time <= end_date)
        .all()
    )
    durations = [e.duration_minutes for e in entries if e.duration_minutes is not None]
    avg_minutes = round(sum(durations) / len(durations), 1) if durations else 0
    return {
        "user_id": user.id,
        "period": f"{start_date.date()} to {end_date.date()}",
        "entries": len(entries),
        "average_duration_minutes": avg_minutes,
        "min_duration_minutes": min(durations) if durations else 0,
        "max_duration_minutes": max(durations) if durations else 0,
    }
