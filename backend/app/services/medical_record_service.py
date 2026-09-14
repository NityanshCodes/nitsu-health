"""Medical record business logic."""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.medical_record import MedicalRecord
from app.models.user import User


def list_records(
    db: Session,
    user: User,
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[MedicalRecord], int]:
    query = db.query(MedicalRecord).filter(MedicalRecord.user_id == user.id)
    if category:
        query = query.filter(MedicalRecord.category == category)
    total = query.count()
    items = query.order_by(MedicalRecord.created_at.desc()).limit(limit).offset(offset).all()
    return items, total


def get_record(db: Session, user: User, record_id: int) -> Optional[MedicalRecord]:
    return (
        db.query(MedicalRecord)
        .filter(MedicalRecord.id == record_id, MedicalRecord.user_id == user.id)
        .first()
    )


def create_record(db: Session, user: User, data, file_path=None, mime_type=None) -> MedicalRecord:
    record = MedicalRecord(
        user_id=user.id,
        category=data.category,
        title=data.title,
        description=data.description,
        file_path=file_path,
        mime_type=mime_type,
        recorded_at=data.recorded_at or datetime.utcnow(),
        notes=data.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_record(db: Session, user: User, record_id: int, data) -> Optional[MedicalRecord]:
    record = get_record(db, user, record_id)
    if record is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


def delete_record(db: Session, user: User, record_id: int) -> bool:
    record = get_record(db, user, record_id)
    if record is None:
        return False
    db.delete(record)
    db.commit()
    return True
