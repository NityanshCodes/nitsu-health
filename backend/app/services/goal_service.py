"""Goal business logic."""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.goal import HealthGoal
from app.models.user import User


def list_goals(
    db: Session,
    user: User,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[HealthGoal], int]:
    query = db.query(HealthGoal).filter(HealthGoal.user_id == user.id)
    if status:
        query = query.filter(HealthGoal.status == status)
    total = query.count()
    items = query.order_by(HealthGoal.created_at.desc()).limit(limit).offset(offset).all()
    return items, total


def get_goal(db: Session, user: User, goal_id: int) -> Optional[HealthGoal]:
    return (
        db.query(HealthGoal)
        .filter(HealthGoal.id == goal_id, HealthGoal.user_id == user.id)
        .first()
    )


def create_goal(db: Session, user: User, data) -> HealthGoal:
    goal = HealthGoal(
        user_id=user.id,
        goal_type=data.goal_type,
        title=data.title,
        target_value=data.target_value,
        unit=data.unit,
        start_date=data.start_date,
        target_date=data.target_date,
        progress_value=data.progress_value,
        status="active",
        notes=data.notes,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def update_goal(db: Session, user: User, goal_id: int, data) -> Optional[HealthGoal]:
    goal = get_goal(db, user, goal_id)
    if goal is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(goal, field, value)
    db.commit()
    db.refresh(goal)
    return goal


def update_progress(db: Session, user: User, goal_id: int, data) -> Optional[HealthGoal]:
    goal = get_goal(db, user, goal_id)
    if goal is None:
        return None
    goal.progress_value = data.progress_value
    if goal.progress_value >= goal.target_value:
        goal.status = "completed"
        goal.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(goal)
    return goal


def delete_goal(db: Session, user: User, goal_id: int) -> bool:
    goal = get_goal(db, user, goal_id)
    if goal is None:
        return False
    db.delete(goal)
    db.commit()
    return True
