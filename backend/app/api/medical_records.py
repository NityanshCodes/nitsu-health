"""Medical records API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.medical_record import (
    MedicalRecordCreate,
    MedicalRecordResponse,
    MedicalRecordUpdate,
)
from app.services import medical_record_service
from app.utils.audit import log_action
from app.utils.auth import get_current_user

router = APIRouter(prefix="/medical-records", tags=["medical-records"])


@router.get("")
def list_records(
    category: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    items, total = medical_record_service.list_records(db, current_user, category, limit, offset)
    return {
        "items": [MedicalRecordResponse.model_validate(r) for r in items],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("", response_model=MedicalRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_record(
    category: str = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(default=None),
    notes: Optional[str] = Form(default=None),
    file: Optional[UploadFile] = File(default=None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MedicalRecordResponse:
    payload = MedicalRecordCreate(
        category=category,
        title=title,
        description=description,
        notes=notes,
    )
    file_path = None
    mime_type = file.content_type if file else None
    if file:
        # Store file path (metadata only; file storage is out of scope this pass)
        file_path = f"uploads/{current_user.id}/{file.filename}"

    record = medical_record_service.create_record(db, current_user, payload, file_path=file_path, mime_type=mime_type)
    log_action(db, "medical_record.create", user_id=current_user.id, entity_type="medical_record", entity_id=record.id)
    return MedicalRecordResponse.model_validate(record)


@router.get("/{record_id}", response_model=MedicalRecordResponse)
def get_record(
    record_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MedicalRecordResponse:
    record = medical_record_service.get_record(db, current_user, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medical record not found")
    return MedicalRecordResponse.model_validate(record)


@router.put("/{record_id}", response_model=MedicalRecordResponse)
def update_record(
    record_id: int,
    payload: MedicalRecordUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MedicalRecordResponse:
    record = medical_record_service.update_record(db, current_user, record_id, payload)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medical record not found")
    return MedicalRecordResponse.model_validate(record)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    deleted = medical_record_service.delete_record(db, current_user, record_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medical record not found")
