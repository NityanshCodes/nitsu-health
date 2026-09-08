from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import DataSource


class SleepEntryCreate(BaseModel):
    start_time: datetime
    end_time: datetime
    duration_minutes: Optional[float] = Field(default=None, ge=0, le=24 * 60)
    sleep_stages: Optional[dict] = None
    source: DataSource = DataSource.MANUAL
    notes: Optional[str] = Field(default=None, max_length=2000)


class SleepEntryUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[float] = Field(default=None, ge=0, le=24 * 60)
    sleep_stages: Optional[dict] = None
    notes: Optional[str] = Field(default=None, max_length=2000)


class SleepEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    start_time: datetime
    end_time: datetime
    duration_minutes: Optional[float] = None
    sleep_stages: Optional[dict] = None
    source: str
    notes: Optional[str] = None