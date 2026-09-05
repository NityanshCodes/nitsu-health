from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.report import HealthReport
from app.utils.auth import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/latest")
def latest_report(current_user=Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    report = (
        db.query(HealthReport)
        .filter(HealthReport.user_id == current_user.id)
        .order_by(HealthReport.created_at.desc())
        .first()
    )
    if not report:
        return {
            "user_id": current_user.id,
            "title": "Latest health report",
            "status": "generated",
            "summary": "No new report yet; the system is ready to generate one.",
        }
    return {
        "user_id": report.user_id,
        "title": report.title,
        "status": report.status,
        "summary": report.summary,
    }
