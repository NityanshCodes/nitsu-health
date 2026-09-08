"""Profile & family-history business logic."""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.family_history import FamilyHistory
from app.models.profile import HealthProfile
from app.models.user import User


def get_health_profile(db: Session, user: User) -> HealthProfile:
    """Return a user's health profile, creating an empty one on first access."""
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == user.id).first()
    if profile is None:
        profile = HealthProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def update_health_profile(db: Session, user: User, data) -> HealthProfile:
    """Update the user's health profile with the provided fields."""
    profile = get_health_profile(db, user)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


def list_family_history(db: Session, user: User) -> list[FamilyHistory]:
    return db.query(FamilyHistory).filter(FamilyHistory.user_id == user.id).order_by(FamilyHistory.id).all()


def create_family_history(db: Session, user: User, data) -> Optional[FamilyHistory]:
    entry = FamilyHistory(
        user_id=user.id,
        category=data.category.value if hasattr(data.category, "value") else data.category,
        relation=data.relation,
        notes=data.notes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def update_family_history(db: Session, user: User, entry_id: int, data) -> Optional[FamilyHistory]:
    entry = db.query(FamilyHistory).filter(FamilyHistory.id == entry_id, FamilyHistory.user_id == user.id).first()
    if entry is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is None:
            continue
        setattr(entry, field, value.value if hasattr(value, "value") else value)
    db.commit()
    db.refresh(entry)
    return entry


def delete_family_history(db: Session, user: User, entry_id: int) -> bool:
    entry = db.query(FamilyHistory).filter(FamilyHistory.id == entry_id, FamilyHistory.user_id == user.id).first()
    if entry is None:
        return False
    db.delete(entry)
    db.commit()
    return True