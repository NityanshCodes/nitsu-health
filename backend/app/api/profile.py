"""Profile & family-history API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.family_history import (
    FamilyHistoryCreate,
    FamilyHistoryResponse,
    FamilyHistoryUpdate,
)
from app.schemas.profile import HealthProfileResponse, HealthProfileUpdate
from app.services import profile_service
from app.utils.auth import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=HealthProfileResponse)
def get_profile(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> HealthProfileResponse:
    profile = profile_service.get_health_profile(db, current_user)
    return HealthProfileResponse.model_validate(profile)


@router.put("", response_model=HealthProfileResponse)
def update_profile(
    data: HealthProfileUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> HealthProfileResponse:
    profile = profile_service.update_health_profile(db, current_user, data)
    return HealthProfileResponse.model_validate(profile)


@router.get("/family-history", response_model=list[FamilyHistoryResponse])
def list_family_history(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[FamilyHistoryResponse]:
    return [FamilyHistoryResponse.model_validate(e) for e in profile_service.list_family_history(db, current_user)]


@router.post("/family-history", response_model=FamilyHistoryResponse, status_code=status.HTTP_201_CREATED)
def create_family_history(
    data: FamilyHistoryCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FamilyHistoryResponse:
    entry = profile_service.create_family_history(db, current_user, data)
    return FamilyHistoryResponse.model_validate(entry)


@router.get("/family-history/{entry_id}", response_model=FamilyHistoryResponse)
def get_family_history(
    entry_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FamilyHistoryResponse:
    entry = profile_service.get_family_history(db, current_user, entry_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family history entry not found")
    return FamilyHistoryResponse.model_validate(entry)


@router.put("/family-history/{entry_id}", response_model=FamilyHistoryResponse)
def update_family_history(
    entry_id: int,
    data: FamilyHistoryUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FamilyHistoryResponse:
    entry = profile_service.update_family_history(db, current_user, entry_id, data)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family history entry not found")
    return FamilyHistoryResponse.model_validate(entry)


@router.delete("/family-history/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_family_history(
    entry_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    deleted = profile_service.delete_family_history(db, current_user, entry_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family history entry not found")