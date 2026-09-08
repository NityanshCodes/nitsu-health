"""AI wellness report generation from real data (observation only)."""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.activity import ActivityEntry
from app.models.goal import HealthGoal
from app.models.health_metric import HealthMetric
from app.models.nutrition import NutritionEntry
from app.models.profile import HealthProfile
from app.models.report import HealthReport
from app.models.sleep import SleepEntry
from app.models.user import User


def generate_report(db: Session, user: User) -> HealthReport:
    """Build a structured wellness report from actual user data."""
    now = datetime.utcnow()
    month_ago = now - timedelta(days=30)

    # Gather data
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == user.id).first()
    metrics = (
        db.query(HealthMetric)
        .filter(HealthMetric.user_id == user.id, HealthMetric.recorded_at >= month_ago)
        .order_by(HealthMetric.recorded_at.desc())
        .all()
    )
    nutrition = (
        db.query(NutritionEntry)
        .filter(NutritionEntry.user_id == user.id, NutritionEntry.consumed_at >= month_ago)
        .all()
    )
    activity = (
        db.query(ActivityEntry)
        .filter(ActivityEntry.user_id == user.id, ActivityEntry.recorded_at >= month_ago)
        .all()
    )
    sleep = (
        db.query(SleepEntry)
        .filter(SleepEntry.user_id == user.id, SleepEntry.start_time >= month_ago)
        .all()
    )
    goals = (
        db.query(HealthGoal)
        .filter(HealthGoal.user_id == user.id, HealthGoal.status == "active")
        .all()
    )

    # Build sections
    sections = {}

    # Profile summary
    if profile:
        sections["profile"] = {
            "height_cm": profile.height_cm,
            "weight_kg": profile.weight_kg,
            "blood_type": profile.blood_type,
            "conditions": profile.medical_conditions,
        }

    # Nutrition
    if nutrition:
        sections["nutrition"] = {
            "entries": len(nutrition),
            "avg_calories": round(sum(e.calories for e in nutrition) / len(nutrition), 1),
            "avg_protein_g": round(sum(e.protein_g for e in nutrition) / len(nutrition), 1),
        }

    # Activity
    if activity:
        sections["activity"] = {
            "entries": len(activity),
            "total_steps": sum(a.steps or 0 for a in activity),
            "total_active_minutes": sum(a.active_minutes or 0 for a in activity),
        }

    # Sleep
    if sleep:
        durations = [s.duration_minutes for s in sleep if s.duration_minutes is not None]
        if durations:
            sections["sleep"] = {
                "nights_logged": len(durations),
                "avg_duration_minutes": round(sum(durations) / len(durations), 1),
            }

    # Goals
    if goals:
        sections["goals"] = [
            {
                "title": g.title,
                "progress_pct": round((g.progress_value / g.target_value) * 100, 1) if g.target_value else 0,
            }
            for g in goals
        ]

    # Metrics summary
    if metrics:
        metric_summary = {}
        for m in metrics:
            if m.metric_type not in metric_summary:
                metric_summary[m.metric_type] = {"count": 0, "values": []}
            metric_summary[m.metric_type]["count"] += 1
            metric_summary[m.metric_type]["values"].append(m.value)
        for k, v in metric_summary.items():
            v["average"] = round(sum(v["values"]) / len(v["values"]), 2)
            del v["values"]
        sections["health_metrics"] = metric_summary

    # Summary
    data_points = len(metrics) + len(nutrition) + len(activity) + len(sleep)
    summary = f"Wellness report for {user.first_name or user.username} covering the past 30 days. "
    summary += f"Total data points collected: {data_points}. "
    if not sections:
        summary += "No significant data logged in this period."

    title = f"Wellness Report — {now.strftime('%B %Y')}"

    report = HealthReport(
        user_id=user.id,
        title=title,
        summary=summary,
        report_data=sections,
        report_type="wellness",
        status="generated",
        generated_at=now,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def list_reports(
    db: Session,
    user: User,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[HealthReport], int]:
    query = db.query(HealthReport).filter(HealthReport.user_id == user.id)
    total = query.count()
    items = query.order_by(HealthReport.created_at.desc()).limit(limit).offset(offset).all()
    return items, total


def get_report(db: Session, user: User, report_id: int) -> Optional[HealthReport]:
    return (
        db.query(HealthReport)
        .filter(HealthReport.id == report_id, HealthReport.user_id == user.id)
        .first()
    )
