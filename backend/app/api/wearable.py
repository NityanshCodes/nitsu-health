from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.wearable import WearableData
from app.utils.auth import get_current_user

router = APIRouter(prefix="/wearables", tags=["wearables"])


@router.get("/status")
def wearable_status(current_user=Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    latest = (
        db.query(WearableData)
        .filter(WearableData.user_id == current_user.id)
        .order_by(WearableData.recorded_at.desc())
        .first()
    )
    if latest:
        return {
            "user_id": current_user.id,
            "status": "connected",
            "provider": latest.source,
            "message": f"Latest wearable metric: {latest.metric_type} = {latest.metric_value} {latest.unit}.",
        }
    return {
        "user_id": current_user.id,
        "status": "not_connected",
        "provider": "none",
        "message": "Wearable integration is ready for the next provider connector.",
    }
