from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.nutrition import NutritionEntry
from app.models.report import HealthReport
from app.models.wearable import WearableData
from app.utils.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(current_user=Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    nutrition_total = db.query(NutritionEntry).filter(NutritionEntry.user_id == current_user.id).count()
    report_total = db.query(HealthReport).filter(HealthReport.user_id == current_user.id).count()
    wearable_total = db.query(WearableData).filter(WearableData.user_id == current_user.id).count()

    insights = [
        "Health records are being tracked for your account only.",
        f"You have {nutrition_total} nutrition entries on file.",
        f"You have {report_total} report record(s) on file.",
        f"You have {wearable_total} wearable record(s) available.",
    ]

    return {
        "user_id": current_user.id,
        "status": "ok",
        "summary": "Dashboard summary is ready for the authenticated user.",
        "insights": insights,
    }
