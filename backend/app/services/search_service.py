"""Unified search across user-owned entities."""

from sqlalchemy.orm import Session

from app.models.activity import ActivityEntry
from app.models.goal import HealthGoal
from app.models.health_metric import HealthMetric
from app.models.medical_record import MedicalRecord
from app.models.nutrition import NutritionEntry
from app.models.report import HealthReport
from app.models.sleep import SleepEntry
from app.models.user import User


def search(db: Session, user: User, q: str, limit: int = 50) -> list[dict]:
    term = f"%{q}%"
    results: list[dict] = []

    # Health metrics
    for m in (
        db.query(HealthMetric)
        .filter(HealthMetric.user_id == user.id)
        .filter(HealthMetric.metric_type.ilike(term) | HealthMetric.notes.ilike(term))
        .limit(limit)
        .all()
    ):
        results.append({"type": "health_metric", "id": m.id, "title": m.metric_type, "detail": m.notes, "date": str(m.recorded_at.date()) if m.recorded_at else None})

    # Nutrition
    for n in (
        db.query(NutritionEntry)
        .filter(NutritionEntry.user_id == user.id)
        .filter(NutritionEntry.meal_type.ilike(term) | NutritionEntry.notes.ilike(term))
        .limit(limit)
        .all()
    ):
        results.append({"type": "nutrition", "id": n.id, "title": n.meal_type, "detail": n.notes, "date": str(n.consumed_at.date())})

    # Activity
    for a in (
        db.query(ActivityEntry)
        .filter(ActivityEntry.user_id == user.id)
        .filter(ActivityEntry.activity_type.ilike(term) | ActivityEntry.notes.ilike(term))
        .limit(limit)
        .all()
    ):
        results.append({"type": "activity", "id": a.id, "title": a.activity_type, "detail": a.notes, "date": str(a.recorded_at.date())})

    # Sleep
    for s in (
        db.query(SleepEntry)
        .filter(SleepEntry.user_id == user.id)
        .filter(SleepEntry.notes.ilike(term))
        .limit(limit)
        .all()
    ):
        results.append({"type": "sleep", "id": s.id, "title": "Sleep entry", "detail": s.notes, "date": str(s.start_time.date())})

    # Goals
    for g in (
        db.query(HealthGoal)
        .filter(HealthGoal.user_id == user.id)
        .filter(HealthGoal.title.ilike(term) | HealthGoal.goal_type.ilike(term) | HealthGoal.notes.ilike(term))
        .limit(limit)
        .all()
    ):
        results.append({"type": "goal", "id": g.id, "title": g.title, "detail": g.notes, "date": str(g.start_date)})

    # Reports
    for r in (
        db.query(HealthReport)
        .filter(HealthReport.user_id == user.id)
        .filter(HealthReport.title.ilike(term) | HealthReport.report_type.ilike(term))
        .limit(limit)
        .all()
    ):
        results.append({"type": "report", "id": r.id, "title": r.title, "detail": r.report_type, "date": str(r.generated_at.date()) if r.generated_at else None})

    # Medical records
    for mr in (
        db.query(MedicalRecord)
        .filter(MedicalRecord.user_id == user.id)
        .filter(MedicalRecord.title.ilike(term) | MedicalRecord.category.ilike(term) | MedicalRecord.notes.ilike(term))
        .limit(limit)
        .all()
    ):
        results.append({"type": "medical_record", "id": mr.id, "title": mr.title, "detail": mr.notes, "date": str(mr.recorded_at.date()) if mr.recorded_at else None})

    return results[:limit]
