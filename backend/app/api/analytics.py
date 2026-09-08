"""Analytics API endpoints (summaries, trends, completeness)."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services import analytics_service
from app.utils.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def summary(
    period: str = Query(default="day", pattern="^(day|week|month)$"),
    target: Optional[datetime] = Query(default=None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Daily/weekly/monthly summary of the user's logged data."""
    try:
        return analytics_service.build_summary(db, current_user, period, target or datetime.utcnow())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.get("/trends/{metric_type}")
def trend(
    metric_type: str,
    days: int = Query(default=14, ge=2, le=90),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return analytics_service.trend(db, current_user, metric_type, days)


@router.get("/goals")
def goal_progress(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    return analytics_service.goal_progress(db, current_user)