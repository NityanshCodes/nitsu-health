from typing import Optional

from pydantic import BaseModel, Field


class NutritionEntryCreate(BaseModel):
    meal_type: str = Field(..., min_length=1, max_length=50)
    calories: float = Field(..., ge=0, le=10000)
    protein_g: float = Field(..., ge=0, le=1000)
    carbs_g: float = Field(..., ge=0, le=1000)
    fats_g: float = Field(..., ge=0, le=1000)
    water_ml: float = Field(..., ge=0, le=20000)
    notes: Optional[str] = Field(default=None, max_length=500)


class NutritionEntryResponse(BaseModel):
    user_id: int
    status: str = "ok"
    calories: int = 0
    water_ml: int = 0
    recommendation: str = "Add a meal log to begin tracking nutrition."
