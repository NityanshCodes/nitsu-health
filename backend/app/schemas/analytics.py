from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class TrendPoint(BaseModel):
    metric_type: str
    value: float
    recorded_at: datetime


class TrendResult(BaseModel):
    metric_type: str
    points: list[TrendPoint]
    direction: Optional[str] = None  # increasing | decreasing | stable | insufficient_data
    percent_change: Optional[float] = None
    note: Optional[str] = None


class SummaryResponse(BaseModel):
    period: str
    target_date: datetime
    nutrition: dict[str, Any]
    activity: dict[str, Any]
    sleep: dict[str, Any]
    completeness: dict[str, Any]


class GoalProgress(BaseModel):
    id: int
    title: str
    progress_percent: Optional[float] = None
    status: str
    on_track: Optional[bool] = None