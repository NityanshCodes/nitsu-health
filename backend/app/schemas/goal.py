from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import GoalStatus


class GoalCreate(BaseModel):
    goal_type: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=200)
    target_value: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=50)
    start_date: date
    target_date: date
    progress_value: float = Field(default=0.0, ge=0)
    notes: Optional[str] = Field(default=None, max_length=2000)


class GoalUpdate(BaseModel):
    goal_type: Optional[str] = Field(default=None, min_length=1, max_length=100)
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    target_value: Optional[float] = Field(default=None, gt=0)
    unit: Optional[str] = Field(default=None, min_length=1, max_length=50)
    target_date: Optional[date] = None
    progress_value: Optional[float] = Field(default=None, ge=0)
    notes: Optional[str] = Field(default=None, max_length=2000)


class GoalProgressUpdate(BaseModel):
    progress_value: float = Field(..., ge=0)


class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    goal_type: str
    title: str
    target_value: float
    unit: str
    start_date: date
    target_date: date
    progress_value: float
    status: str
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None
