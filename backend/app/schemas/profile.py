from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class HealthProfileBase(BaseModel):
    height_cm: Optional[float] = Field(default=None, ge=50, le=300)
    weight_kg: Optional[float] = Field(default=None, ge=20, le=500)
    blood_type: Optional[str] = Field(default=None, max_length=10)
    medical_conditions: Optional[str] = Field(default=None, max_length=500)
    allergies: Optional[str] = Field(default=None, max_length=2000)
    medications: Optional[str] = Field(default=None, max_length=2000)
    lifestyle: Optional[str] = Field(default=None, max_length=2000)
    health_notes: Optional[str] = Field(default=None, max_length=2000)


class HealthProfileUpdate(HealthProfileBase):
    pass


class HealthProfileResponse(HealthProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int