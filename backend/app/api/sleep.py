"""Sleep API endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.sleep import (
    SleepEntryCreate,
    SleepEntryResponse,
    SleepEntryUpdate,
)
from app.services import sleep_service
from app.utils.audit import log_action
from app.utils.auth import get_current_user

router = APIRouter(prefix="/sleep", tags=["sleep"])


@router.get("/weekly")
def sleep_weekly(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return sleep_service.weekly_average(db, current_user)


@router.get("")
def list_sleep(
    day: Optional[datetime] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    items, total = sleep_service.list_entries(db, current_user, day, limit, offset)
    return {
        "items": [SleepEntryResponse.model_validate(e) for e in items],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("", response_model=SleepEntryResponse, status_code=status.HTTP_201_CREATED)
def create_sleep_entry(
    payload: SleepEntryCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SleepEntryResponse:
    entry = sleep_service.create_entry(db, current_user, payload)
    log_action(db, "sleep.create", user_id=current_user.id, entity_type="sleep_entry", entity_id=entry.id)
    return SleepEntryResponse.model_validate(entry)


@router.get("/{entry_id}", response_model=SleepEntryResponse)
def get_sleep_entry(
    entry_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SleepEntryResponse:
    entry = sleep_service.get_entry(db, current_user, entry_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sleep entry not found")
    return SleepEntryResponse.model_validate(entry)


@router.put("/{entry_id}", response_model=SleepEntryResponse)
def update_sleep_entry(
    entry_id: int,
    payload: SleepEntryUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SleepEntryResponse:
    entry = sleep_service.update_entry(db, current_user, entry_id, payload)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sleep entry not found")
    return SleepEntryResponse.model_validate(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sleep_entry(
    entry_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    deleted = sleep_service.delete_entry(db, current_user, entry_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sleep entry not found")
