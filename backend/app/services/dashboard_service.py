"""Dashboard — aggregated overview scoped to the current user."""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.activity import ActivityEntry
from app.models.goal import HealthGoal
from app.models.health_metric import HealthMetric
from app.models.nutrition import NutritionEntry
from app.models.notification import Notification
from app.models.report import HealthReport
from app.models.sleep import SleepEntry
from app.models.user import User
from app.services import nutrition_service


def overview(db: Session, user: User) -> dict:
    now = datetime.utcnow()
    today_start = datetime.combine(now.date(), datetime.min.time())
    week_ago = now - timedelta(days=7)

    # Today's nutrition
    nutrition_today = nutrition_service.daily_summary(db, user, now)

    # Today's activity
    today_activities = (
        db.query(ActivityEntry)
        .filter(ActivityEntry.user_id == user.id, ActivityEntry.recorded_at >= today_start)
        .all()
    )
    activity_summary = {
        "entries": len(today_activities),
        "total_steps": sum(e.steps or 0 for e in today_activities),
        "total_active_minutes": sum(e.active_minutes or 0 for e in today_activities),
    }

    # Recent sleep (last entry)
    last_sleep = (
        db.query(SleepEntry)
        .filter(SleepEntry.user_id == user.id)
        .order_by(SleepEntry.start_time.desc())
        .first()
    )
    sleep_summary = {
        "last_entry": {
            "duration_minutes": last_sleep.duration_minutes if last_sleep else None,
            "start_time": str(last_sleep.start_time) if last_sleep else None,
        }
    }

    # Active goals with progress
    active_goals = (
        db.query(HealthGoal)
        .filter(HealthGoal.user_id == user.id, HealthGoal.status == "active")
        .order_by(HealthGoal.created_at.desc())
        .limit(5)
        .all()
    )
    goals = [
        {
            "id": g.id,
            "title": g.title,
            "target_value": g.target_value,
            "progress_value": g.progress_value,
            "unit": g.unit,
            "progress_pct": round((g.progress_value / g.target_value) * 100, 1) if g.target_value else 0,
        }
        for g in active_goals
    ]

    # Recent reports
    recent_reports = (
        db.query(HealthReport)
        .filter(HealthReport.user_id == user.id)
        .order_by(HealthReport.created_at.desc())
        .limit(3)
        .all()
    )
    reports = [{"id": r.id, "title": r.title, "report_type": r.report_type, "created_at": str(r.created_at)} for r in recent_reports]

    # Unread notification count
    unread_notifications = (
        db.query(Notification)
        .filter(Notification.user_id == user.id, Notification.is_read == False)
        .count()
    )

    # Latest health metrics
    latest_metrics = (
        db.query(HealthMetric)
        .filter(HealthMetric.user_id == user.id)
        .order_by(HealthMetric.recorded_at.desc())
        .limit(5)
        .all()
    )
    metrics = [
        {"metric_type": m.metric_type, "value": m.value, "unit": m.unit, "recorded_at": str(m.recorded_at)}
        for m in latest_metrics
    ]

    return {
        "user_id": user.id,
        "nutrition_today": nutrition_today,
        "activity_today": activity_summary,
        "sleep": sleep_summary,
        "active_goals": goals,
        "recent_reports": reports,
        "unread_notifications": unread_notifications,
        "latest_metrics": metrics,
    }
