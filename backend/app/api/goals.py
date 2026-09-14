"""Goals API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.goal import (
    GoalCreate,
    GoalProgressUpdate,
    GoalResponse,
    GoalUpdate,
)
from app.services import goal_service
from app.utils.audit import log_action
from app.utils.auth import get_current_user

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("")
def list_goals(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    items, total = goal_service.list_goals(db, current_user, status_filter, limit, offset)
    return {
        "items": [GoalResponse.model_validate(g) for g in items],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    payload: GoalCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GoalResponse:
    goal = goal_service.create_goal(db, current_user, payload)
    log_action(db, "goal.create", user_id=current_user.id, entity_type="health_goal", entity_id=goal.id)
    return GoalResponse.model_validate(goal)


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(
    goal_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GoalResponse:
    goal = goal_service.get_goal(db, current_user, goal_id)
    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return GoalResponse.model_validate(goal)


@router.put("/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: int,
    payload: GoalUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GoalResponse:
    goal = goal_service.update_goal(db, current_user, goal_id, payload)
    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return GoalResponse.model_validate(goal)


@router.post("/{goal_id}/progress", response_model=GoalResponse)
def update_goal_progress(
    goal_id: int,
    payload: GoalProgressUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GoalResponse:
    goal = goal_service.update_progress(db, current_user, goal_id, payload)
    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return GoalResponse.model_validate(goal)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    deleted = goal_service.delete_goal(db, current_user, goal_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
