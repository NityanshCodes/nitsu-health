"""Health metric CRUD and trend computation."""

from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.health_metric import HealthMetric
from app.models.user import User


def list_metrics(
    db: Session,
    user: User,
    metric_type: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[HealthMetric], int]:
    query = db.query(HealthMetric).filter(HealthMetric.user_id == user.id)
    if metric_type:
        query = query.filter(HealthMetric.metric_type == metric_type)
    if start:
        query = query.filter(HealthMetric.recorded_at >= start)
    if end:
        query = query.filter(HealthMetric.recorded_at <= end)

    total = query.count()
    items = (
        query.order_by(HealthMetric.recorded_at.desc(), HealthMetric.id.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return items, total


def get_metric(db: Session, user: User, metric_id: int) -> Optional[HealthMetric]:
    return (
        db.query(HealthMetric)
        .filter(HealthMetric.id == metric_id, HealthMetric.user_id == user.id)
        .first()
    )


def create_metric(db: Session, user: User, data) -> HealthMetric:
    metric = HealthMetric(
        user_id=user.id,
        metric_type=data.metric_type,
        value=data.value,
        unit=data.unit,
        source=data.source.value if hasattr(data.source, "value") else data.source,
        recorded_at=data.recorded_at or datetime.utcnow(),
        notes=data.notes,
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


def update_metric(db: Session, user: User, metric_id: int, data) -> Optional[HealthMetric]:
    metric = get_metric(db, user, metric_id)
    if metric is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(metric, field, value)
    db.commit()
    db.refresh(metric)
    return metric


def delete_metric(db: Session, user: User, metric_id: int) -> bool:
    metric = get_metric(db, user, metric_id)
    if metric is None:
        return False
    db.delete(metric)
    db.commit()
    return True


def metric_types(db: Session, user: User) -> list[str]:
    rows = (
        db.query(HealthMetric.metric_type)
        .filter(HealthMetric.user_id == user.id)
        .distinct()
        .order_by(HealthMetric.metric_type)
        .all()
    )
    return [r[0] for r in rows]


def get_series(
    db: Session,
    user: User,
    metric_type: str,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> list[HealthMetric]:
    """Chronological series for a metric type (used by analytics/trends)."""
    query = (
        db.query(HealthMetric)
        .filter(HealthMetric.user_id == user.id, HealthMetric.metric_type == metric_type)
        .order_by(HealthMetric.recorded_at.asc())
    )
    if start:
        query = query.filter(HealthMetric.recorded_at >= start)
    if end:
        query = query.filter(HealthMetric.recorded_at <= end)
    return query.all()


def summary_stats(db: Session, user: User, metric_type: str) -> Optional[dict]:
    """Simple descriptive statistics for one metric type (observation only)."""
    values = [m.value for m in get_series(db, user, metric_type)]
    if not values:
        return None
    n = len(values)
    mean = sum(values) / n
    return {
        "metric_type": metric_type,
        "count": n,
        "min": min(values),
        "max": max(values),
        "mean": round(mean, 4),
        "latest": values[-1],
        "earliest": values[0],
        "unit": get_series(db, user, metric_type)[-1].unit,
    }