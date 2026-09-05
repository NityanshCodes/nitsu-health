from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.nutrition import NutritionEntry
from app.schemas.nutrition import NutritionEntryCreate, NutritionEntryResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


@router.get("/today", response_model=NutritionEntryResponse)
def nutrition_today(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NutritionEntryResponse:
    today = datetime.utcnow().date()
    entry = (
        db.query(NutritionEntry)
        .filter(NutritionEntry.user_id == current_user.id)
        .order_by(NutritionEntry.consumed_at.desc())
        .first()
    )
    if not entry:
        return NutritionEntryResponse(
            user_id=current_user.id,
            status="ok",
            calories=0,
            water_ml=0,
            recommendation="Add a meal log to begin tracking nutrition.",
        )
    return NutritionEntryResponse(
        user_id=current_user.id,
        status="ok",
        calories=int(entry.calories),
        water_ml=int(entry.water_ml),
        recommendation="Hydration and calories are being tracked for the current day.",
    )


@router.post("", response_model=NutritionEntryCreate)
def create_nutrition_entry(
    payload: NutritionEntryCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NutritionEntryCreate:
    entry = NutritionEntry(
        user_id=current_user.id,
        meal_type=payload.meal_type,
        calories=payload.calories,
        protein_g=payload.protein_g,
        carbs_g=payload.carbs_g,
        fats_g=payload.fats_g,
        water_ml=payload.water_ml,
        notes=payload.notes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return NutritionEntryCreate(**entry.__dict__)
