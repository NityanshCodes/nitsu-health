"""Conservative analytics: summaries, trends, completeness.

All outputs are framed as observations (e.g. "recorded sleep duration has
decreased over two weeks") — never as interpretations or diagnoses.
"""

from datetime import datetime, time, timedelta
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.activity import ActivityEntry
from app.models.health_metric import HealthMetric
from app.models.nutrition import NutritionEntry
from app.models.sleep import SleepEntry
from app.models.user import User


def _day_start(day: datetime) -> datetime:
    return datetime.combine(day.date(), time.min)


def _day_end(day: datetime) -> datetime:
    return datetime.combine(day.date(), time.max)


def _sum_field(query, model, field):
    return query.with_entities(func.coalesce(func.sum(getattr(model, field)), 0)).scalar()


def build_summary(db: Session, user: User, period: str, target: datetime) -> dict:
    """Build a daily/weekly/monthly summary for the given period."""
    if period == "day":
        start = _day_start(target)
        end = _day_end(target)
    elif period == "week":
        week_start = target.date() - timedelta(days=target.weekday())
        start = datetime.combine(week_start, time.min)
        end = start + timedelta(days=7)
    elif period == "month":
        month_start = target.date().replace(day=1)
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        start = datetime.combine(month_start, time.min)
        end = datetime.combine(next_month, time.min)
    else:
        raise ValueError(f"Unsupported period: {period}")

    nutrition_query = db.query(NutritionEntry).filter(NutritionEntry.user_id == user.id, NutritionEntry.consumed_at >= start, NutritionEntry.consumed_at < end)
    nutrition = {
        "entries": nutrition_query.count(),
        "calories": float(_sum_field(nutrition_query, NutritionEntry, "calories")),
        "protein_g": float(_sum_field(nutrition_query, NutritionEntry, "protein_g")),
        "carbs_g": float(_sum_field(nutrition_query, NutritionEntry, "carbs_g")),
        "fats_g": float(_sum_field(nutrition_query, NutritionEntry, "fats_g")),
        "water_ml": float(_sum_field(nutrition_query, NutritionEntry, "water_ml")),
    }

    activity_query = db.query(ActivityEntry).filter(ActivityEntry.user_id == user.id, ActivityEntry.recorded_at >= start, ActivityEntry.recorded_at < end)
    activity = {
        "entries": activity_query.count(),
        "steps": int(_sum_field(activity_query, ActivityEntry, "steps")),
        "active_minutes": int(_sum_field(activity_query, ActivityEntry, "active_minutes")),
        "distance_km": float(_sum_field(activity_query, ActivityEntry, "distance_km")),
        "calories_burned": float(_sum_field(activity_query, ActivityEntry, "calories_burned")),
    }

    sleep_query = db.query(SleepEntry).filter(SleepEntry.user_id == user.id, SleepEntry.start_time >= start, SleepEntry.start_time < end)
    avg_duration = (
        sleep_query.with_entities(func.avg(SleepEntry.duration_minutes)).scalar()
    )
    sleep = {
        "entries": sleep_query.count(),
        "avg_duration_minutes": round(float(avg_duration), 2) if avg_duration is not None else None,
        "note": "Sleep stage data reflects wearable-derived information when present.",
    }

    completeness = _completeness(db, user, start, end, period)

    return {
        "period": period,
        "target_date": target,
        "nutrition": nutrition,
        "activity": activity,
        "sleep": sleep,
        "completeness": completeness,
    }


def _completeness(db: Session, user: User, start: datetime, end: datetime, period: str) -> dict:
    """Data-completeness indicator across domains for the window."""
    days = (end - start).days or 1
    nutrition_days = (
        db.query(func.count(func.distinct(func.date(NutritionEntry.consumed_at))))
        .filter(NutritionEntry.user_id == user.id, NutritionEntry.consumed_at >= start, NutritionEntry.consumed_at < end)
        .scalar()
    )
    activity_days = (
        db.query(func.count(func.distinct(func.date(ActivityEntry.recorded_at))))
        .filter(ActivityEntry.user_id == user.id, ActivityEntry.recorded_at >= start, ActivityEntry.recorded_at < end)
        .scalar()
    )
    sleep_days = (
        db.query(func.count(func.distinct(func.date(SleepEntry.start_time))))
        .filter(SleepEntry.user_id == user.id, SleepEntry.start_time >= start, SleepEntry.start_time < end)
        .scalar()
    )
    return {
        "days_in_window": days,
        "nutrition_days": int(nutrition_days or 0),
        "activity_days": int(activity_days or 0),
        "sleep_days": int(sleep_days or 0),
        "nutrition_pct": round(((nutrition_days or 0) / days) * 100, 1),
        "activity_pct": round(((activity_days or 0) / days) * 100, 1),
        "sleep_pct": round(((sleep_days or 0) / days) * 100, 1),
    }


def trend(
    db: Session,
    user: User,
    metric_type: str,
    days: int = 14,
) -> dict:
    """Detect direction of a metric series over a window (observation only)."""
    start = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(HealthMetric)
        .filter(
            HealthMetric.user_id == user.id,
            HealthMetric.metric_type == metric_type,
            HealthMetric.recorded_at >= start,
        )
        .order_by(HealthMetric.recorded_at.asc())
        .all()
    )

    if len(rows) < 2:
        return {
            "metric_type": metric_type,
            "points": [],
            "direction": "insufficient_data",
            "note": "Not enough recorded data to estimate a trend.",
        }

    values = [r.value for r in rows]
    first, last = values[0], values[-1]

    if first == 0:
        direction = "stable" if last == 0 else "increasing"
        percent_change = None
    else:
        percent_change = round(((last - first) / abs(first)) * 100, 1)
        if percent_change > 3:
            direction = "increasing"
        elif percent_change < -3:
            direction = "decreasing"
        else:
            direction = "stable"

    return {
        "metric_type": metric_type,
        "points": [
            {"metric_type": metric_type, "value": r.value, "recorded_at": r.recorded_at.isoformat()}
            for r in rows
        ],
        "direction": direction,
        "percent_change": percent_change,
        "note": (
            f"Your recorded {metric_type} has trended {direction} between the first and last "
            "recorded values in this window. This is an observation of your logged data, "
            "not a medical interpretation."
        ),
    }


def goal_progress(db: Session, user: User) -> list[dict]:
    """Progress for active goals."""
    from app.models.goal import HealthGoal

    goals = (
        db.query(HealthGoal)
        .filter(HealthGoal.user_id == user.id, HealthGoal.status == "active")
        .all()
    )
    result = []
    for goal in goals:
        pct = None
        if goal.target_value not in (None, 0) and goal.progress_value is not None:
            pct = round((goal.progress_value / goal.target_value) * 100, 1)
        on_track = None
        if pct is not None:
            on_track = pct >= 50
        result.append(
            {
                "id": goal.id,
                "title": goal.title,
                "progress_percent": pct,
                "status": goal.status,
                "on_track": on_track,
            }
        )
    return result