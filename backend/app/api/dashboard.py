"""Dashboard API endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services import dashboard_service
from app.utils.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def get_dashboard(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return dashboard_service.overview(db, current_user)
