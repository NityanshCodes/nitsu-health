"""Nutrition API endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.nutrition import (
    NutritionEntryCreate,
    NutritionEntryResponse,
    NutritionEntryUpdate,
)
from app.services import nutrition_service
from app.utils.audit import log_action
from app.utils.auth import get_current_user

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


@router.get("/today")
def nutrition_today(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """True daily aggregate for today (not just the latest entry)."""
    result = nutrition_service.daily_summary(db, current_user)
    result["status"] = "ok"
    return result


@router.get("")
def list_nutrition(
    day: Optional[datetime] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    items, total = nutrition_service.list_entries(db, current_user, day, limit, offset)
    return {
        "items": [NutritionEntryResponse.model_validate(e) for e in items],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("", response_model=NutritionEntryResponse, status_code=status.HTTP_201_CREATED)
def create_nutrition_entry(
    payload: NutritionEntryCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NutritionEntryResponse:
    entry = nutrition_service.create_entry(db, current_user, payload)
    log_action(db, "nutrition.create", user_id=current_user.id, entity_type="nutrition_entry", entity_id=entry.id)
    return NutritionEntryResponse.model_validate(entry)


@router.get("/trends")
def nutrition_trends(
    metric: str = Query(default="calories"),
    days: int = Query(default=30, ge=1, le=90),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return nutrition_service.trend(db, current_user, metric, days)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.get("/{entry_id}", response_model=NutritionEntryResponse)
def get_nutrition_entry(
    entry_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NutritionEntryResponse:
    entry = nutrition_service.get_entry(db, current_user, entry_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutrition entry not found")
    return NutritionEntryResponse.model_validate(entry)


@router.put("/{entry_id}", response_model=NutritionEntryResponse)
def update_nutrition_entry(
    entry_id: int,
    payload: NutritionEntryUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NutritionEntryResponse:
    entry = nutrition_service.update_entry(db, current_user, entry_id, payload)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutrition entry not found")
    return NutritionEntryResponse.model_validate(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nutrition_entry(
    entry_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    deleted = nutrition_service.delete_entry(db, current_user, entry_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutrition entry not found")