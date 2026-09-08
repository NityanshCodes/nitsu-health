"""Nutrition entry schemas."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class NutritionEntryCreate(BaseModel):
    meal_type: str = Field(..., min_length=1, max_length=50)
    calories: float = Field(..., ge=0, le=10000)
    protein_g: float = Field(..., ge=0, le=1000)
    carbs_g: float = Field(..., ge=0, le=1000)
    fats_g: float = Field(..., ge=0, le=1000)
    fiber_g: float = Field(default=0, ge=0, le=1000)
    water_ml: float = Field(..., ge=0, le=20000)
    consumed_at: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, max_length=500)


class NutritionEntryUpdate(BaseModel):
    meal_type: Optional[str] = Field(default=None, min_length=1, max_length=50)
    calories: Optional[float] = Field(default=None, ge=0, le=10000)
    protein_g: Optional[float] = Field(default=None, ge=0, le=1000)
    carbs_g: Optional[float] = Field(default=None, ge=0, le=1000)
    fats_g: Optional[float] = Field(default=None, ge=0, le=1000)
    fiber_g: Optional[float] = Field(default=None, ge=0, le=1000)
    water_ml: Optional[float] = Field(default=None, ge=0, le=20000)
    consumed_at: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, max_length=500)


class NutritionEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    meal_type: str
    calories: float
    protein_g: float
    carbs_g: float
    fats_g: float
    fiber_g: float = 0
    water_ml: float
    consumed_at: datetime
    notes: Optional[str] = None


class DailyNutritionResponse(BaseModel):
    user_id: int
    date: date
    entries: int = 0
    calories: float = 0
    protein_g: float = 0
    carbs_g: float = 0
    fats_g: float = 0
    fiber_g: float = 0
    water_ml: float = 0
    recommendation: str = "Log a meal to start tracking your nutrition."


class NutritionTrendResponse(BaseModel):
    metric: str  # calories | water_ml | protein_g ...
    days: list[dict]