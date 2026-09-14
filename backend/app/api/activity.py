"""Activity API endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.activity import (
    ActivityEntryCreate,
    ActivityEntryResponse,
    ActivityEntryUpdate,
)
from app.services import activity_service
from app.utils.audit import log_action
from app.utils.auth import get_current_user

router = APIRouter(prefix="/activity", tags=["activity"])


@router.get("/today")
def activity_today(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return activity_service.daily_summary(db, current_user)


@router.get("/weekly")
def activity_weekly(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return activity_service.weekly_summary(db, current_user)


@router.get("")
def list_activity(
    day: Optional[datetime] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    items, total = activity_service.list_entries(db, current_user, day, limit, offset)
    return {
        "items": [ActivityEntryResponse.model_validate(e) for e in items],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("", response_model=ActivityEntryResponse, status_code=status.HTTP_201_CREATED)
def create_activity_entry(
    payload: ActivityEntryCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ActivityEntryResponse:
    entry = activity_service.create_entry(db, current_user, payload)
    log_action(db, "activity.create", user_id=current_user.id, entity_type="activity_entry", entity_id=entry.id)
    return ActivityEntryResponse.model_validate(entry)


@router.get("/{entry_id}", response_model=ActivityEntryResponse)
def get_activity_entry(
    entry_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ActivityEntryResponse:
    entry = activity_service.get_entry(db, current_user, entry_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity entry not found")
    return ActivityEntryResponse.model_validate(entry)


@router.put("/{entry_id}", response_model=ActivityEntryResponse)
def update_activity_entry(
    entry_id: int,
    payload: ActivityEntryUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ActivityEntryResponse:
    entry = activity_service.update_entry(db, current_user, entry_id, payload)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity entry not found")
    return ActivityEntryResponse.model_validate(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity_entry(
    entry_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    deleted = activity_service.delete_entry(db, current_user, entry_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity entry not found")
