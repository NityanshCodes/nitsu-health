"""Nutrition entry business logic."""

from datetime import datetime, time, timedelta
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.nutrition import NutritionEntry
from app.models.user import User


def _day_bounds(day: datetime) -> tuple[datetime, datetime]:
    start = datetime.combine(day.date(), time.min)
    end = datetime.combine(day.date(), time.max)
    return start, end


def daily_summary(db: Session, user: User, day: Optional[datetime] = None) -> dict:
    """Aggregate all nutrition entries for one day (true daily sums)."""
    day = day or datetime.utcnow()
    start, end = _day_bounds(day)
    query = db.query(NutritionEntry).filter(
        NutritionEntry.user_id == user.id,
        NutritionEntry.consumed_at >= start,
        NutritionEntry.consumed_at <= end,
    )
    entries = query.all()
    return {
        "user_id": user.id,
        "date": day.date(),
        "entries": len(entries),
        "calories": round(sum(e.calories for e in entries), 1),
        "protein_g": round(sum(e.protein_g for e in entries), 1),
        "carbs_g": round(sum(e.carbs_g for e in entries), 1),
        "fats_g": round(sum(e.fats_g for e in entries), 1),
        "fiber_g": round(sum(e.fiber_g for e in entries), 1),
        "water_ml": round(sum(e.water_ml for e in entries), 1),
        "recommendation": (
            "Log a meal to start tracking your nutrition."
            if not entries
            else "Here is today's recorded nutrition summary."
        ),
    }


def list_entries(
    db: Session,
    user: User,
    day: Optional[datetime] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[NutritionEntry], int]:
    query = db.query(NutritionEntry).filter(NutritionEntry.user_id == user.id)
    if day:
        start, end = _day_bounds(day)
        query = query.filter(NutritionEntry.consumed_at >= start, NutritionEntry.consumed_at <= end)
    total = query.count()
    items = (
        query.order_by(NutritionEntry.consumed_at.desc(), NutritionEntry.id.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return items, total


def get_entry(db: Session, user: User, entry_id: int) -> Optional[NutritionEntry]:
    return (
        db.query(NutritionEntry)
        .filter(NutritionEntry.id == entry_id, NutritionEntry.user_id == user.id)
        .first()
    )


def create_entry(db: Session, user: User, data) -> NutritionEntry:
    entry = NutritionEntry(
        user_id=user.id,
        meal_type=data.meal_type,
        calories=data.calories,
        protein_g=data.protein_g,
        carbs_g=data.carbs_g,
        fats_g=data.fats_g,
        fiber_g=data.fiber_g,
        water_ml=data.water_ml,
        consumed_at=data.consumed_at or datetime.utcnow(),
        notes=data.notes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def update_entry(db: Session, user: User, entry_id: int, data) -> Optional[NutritionEntry]:
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


def trend(db: Session, user: User, metric: str, days: int = 30) -> dict:
    """Daily totals for a nutrition metric over a window (observation only)."""
    metric_map = {
        "calories": NutritionEntry.calories,
        "protein_g": NutritionEntry.protein_g,
        "carbs_g": NutritionEntry.carbs_g,
        "fats_g": NutritionEntry.fats_g,
        "fiber_g": NutritionEntry.fiber_g,
        "water_ml": NutritionEntry.water_ml,
    }
    column = metric_map.get(metric)
    if column is None:
        raise ValueError(f"Unsupported nutrition metric: {metric}")

    start = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(func.date(NutritionEntry.consumed_at).label("day"), func.sum(column).label("total"))
        .filter(NutritionEntry.user_id == user.id, NutritionEntry.consumed_at >= start)
        .group_by(func.date(NutritionEntry.consumed_at))
        .order_by(func.date(NutritionEntry.consumed_at))
        .all()
    )
    return {
        "metric": metric,
        "days": [{"date": r.day, "total": round(float(r.total), 1)} for r in rows],
    }