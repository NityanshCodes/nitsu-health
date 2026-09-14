"""AI insights — derive observations from real user data (no fabrication)."""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.activity import ActivityEntry
from app.models.ai_insight import AIInsight
from app.models.goal import HealthGoal
from app.models.health_metric import HealthMetric
from app.models.nutrition import NutritionEntry
from app.models.sleep import SleepEntry
from app.models.user import User


def generate_insights(db: Session, user: User) -> list[AIInsight]:
    """Scan recent data and create observation-based insights.

    Each insight references source data and uses conservative framing.
    """
    generated: list[AIInsight] = []
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # --- Activity trend ---
    week_activities = (
        db.query(ActivityEntry)
        .filter(ActivityEntry.user_id == user.id, ActivityEntry.recorded_at >= week_ago)
        .all()
    )
    if week_activities:
        total_steps = sum(a.steps or 0 for a in week_activities)
        avg_steps = total_steps // max(len(week_activities), 1)
        insight = AIInsight(
            user_id=user.id,
            insight_type="activity",
            title="Weekly activity summary",
            body=f"Over the past 7 days, you logged {len(week_activities)} activity entries with an average of {avg_steps} steps per entry.",
            source_data={"total_steps": total_steps, "entries": len(week_activities), "avg_steps": avg_steps},
            confidence=1.0,
            next_step="Consider setting a weekly step goal if you don't have one.",
        )
        db.add(insight)
        generated.append(insight)

    # --- Sleep pattern ---
    week_sleep = (
        db.query(SleepEntry)
        .filter(SleepEntry.user_id == user.id, SleepEntry.start_time >= week_ago)
        .all()
    )
    durations = [s.duration_minutes for s in week_sleep if s.duration_minutes is not None]
    if durations:
        avg_sleep = sum(durations) / len(durations)
        insight = AIInsight(
            user_id=user.id,
            insight_type="sleep",
            title="Weekly sleep pattern",
            body=f"Your average sleep duration over {len(durations)} nights was {avg_sleep:.0f} minutes ({avg_sleep/60:.1f} hours).",
            source_data={"nights": len(durations), "avg_minutes": round(avg_sleep, 1)},
            confidence=1.0,
            next_step="Consistent sleep schedules support overall wellbeing.",
        )
        db.add(insight)
        generated.append(insight)

    # --- Nutrition completeness ---
    week_nutrition = (
        db.query(NutritionEntry)
        .filter(NutritionEntry.user_id == user.id, NutritionEntry.consumed_at >= week_ago)
        .all()
    )
    if week_nutrition:
        avg_cal = sum(e.calories for e in week_nutrition) / len(week_nutrition)
        insight = AIInsight(
            user_id=user.id,
            insight_type="nutrition",
            title="Nutrition logging consistency",
            body=f"You logged {len(week_nutrition)} nutrition entries this week with an average of {avg_cal:.0f} calories per entry.",
            source_data={"entries": len(week_nutrition), "avg_calories": round(avg_cal, 1)},
            confidence=1.0,
        )
        db.add(insight)
        generated.append(insight)

    # --- Goal progress ---
    active_goals = (
        db.query(HealthGoal)
        .filter(HealthGoal.user_id == user.id, HealthGoal.status == "active")
        .all()
    )
    for g in active_goals:
        pct = (g.progress_value / g.target_value * 100) if g.target_value else 0
        if pct > 0:
            insight = AIInsight(
                user_id=user.id,
                insight_type="goal",
                title=f"Progress on: {g.title}",
                body=f"Your current progress is {pct:.0f}% towards your target of {g.target_value} {g.unit}.",
                source_data={"goal_id": g.id, "progress": g.progress_value, "target": g.target_value, "pct": round(pct, 1)},
                confidence=1.0,
            )
            db.add(insight)
            generated.append(insight)

    # --- Health metric observations ---
    month_metrics = (
        db.query(HealthMetric)
        .filter(HealthMetric.user_id == user.id, HealthMetric.recorded_at >= month_ago)
        .all()
    )
    metric_types = set(m.metric_type for m in month_metrics)
    for mt in metric_types:
        values = [m.value for m in month_metrics if m.metric_type == mt]
        if len(values) >= 2:
            avg_val = sum(values) / len(values)
            insight = AIInsight(
                user_id=user.id,
                insight_type="health_metric",
                title=f"{mt} observations",
                body=f"Your {mt} has been recorded {len(values)} times this month with an average of {avg_val:.1f}.",
                source_data={"metric_type": mt, "count": len(values), "average": round(avg_val, 2)},
                confidence=1.0,
            )
            db.add(insight)
            generated.append(insight)

    if generated:
        db.commit()
        for i in generated:
            db.refresh(i)

    return generated


def list_insights(
    db: Session,
    user: User,
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[AIInsight], int]:
    query = db.query(AIInsight).filter(AIInsight.user_id == user.id)
    if unread_only:
        query = query.filter(AIInsight.is_read == False)
    total = query.count()
    items = query.order_by(AIInsight.generated_at.desc()).limit(limit).offset(offset).all()
    return items, total


def mark_read(db: Session, user: User, insight_id: int) -> Optional[AIInsight]:
    insight = (
        db.query(AIInsight)
        .filter(AIInsight.id == insight_id, AIInsight.user_id == user.id)
        .first()
    )
    if insight is None:
        return None
    insight.is_read = True
    db.commit()
    db.refresh(insight)
    return insight
