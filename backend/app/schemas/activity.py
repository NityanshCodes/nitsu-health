from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import DataSource


class ActivityEntryCreate(BaseModel):
    activity_type: str = Field(..., min_length=1, max_length=100)
    steps: Optional[int] = Field(default=None, ge=0, le=1_000_000)
    active_minutes: Optional[int] = Field(default=None, ge=0, le=24 * 60)
    distance_km: Optional[float] = Field(default=None, ge=0, le=10000)
    calories_burned: Optional[float] = Field(default=None, ge=0, le=100000)
    source: DataSource = DataSource.MANUAL
    recorded_at: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, max_length=2000)


class ActivityEntryUpdate(BaseModel):
    activity_type: Optional[str] = Field(default=None, min_length=1, max_length=100)
    steps: Optional[int] = Field(default=None, ge=0, le=1_000_000)
    active_minutes: Optional[int] = Field(default=None, ge=0, le=24 * 60)
    distance_km: Optional[float] = Field(default=None, ge=0, le=10000)
    calories_burned: Optional[float] = Field(default=None, ge=0, le=100000)
    recorded_at: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, max_length=2000)


class ActivityEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    activity_type: str
    steps: Optional[int] = None
    active_minutes: Optional[int] = None
    distance_km: Optional[float] = None
    calories_burned: Optional[float] = None
    source: str
    recorded_at: datetime
    notes: Optional[str] = None