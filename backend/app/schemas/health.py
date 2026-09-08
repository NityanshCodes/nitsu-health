from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import DataSource


class HealthMetricCreate(BaseModel):
    metric_type: str = Field(..., min_length=1, max_length=100)
    value: float = Field(..., ge=0)
    unit: str = Field(..., min_length=1, max_length=50)
    source: DataSource = DataSource.MANUAL
    recorded_at: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, max_length=2000)


class HealthMetricUpdate(BaseModel):
    value: Optional[float] = Field(default=None, ge=0)
    unit: Optional[str] = Field(default=None, max_length=50)
    recorded_at: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, max_length=2000)


class HealthMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    metric_type: str
    value: float
    unit: str
    source: str
    recorded_at: datetime
    notes: Optional[str] = None