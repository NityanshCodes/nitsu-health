from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MedicalRecordCreate(BaseModel):
    category: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    recorded_at: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, max_length=2000)


class MedicalRecordUpdate(BaseModel):
    category: Optional[str] = Field(default=None, min_length=1, max_length=100)
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    recorded_at: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, max_length=2000)


class MedicalRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    category: str
    title: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    mime_type: Optional[str] = None
    recorded_at: Optional[datetime] = None
    notes: Optional[str] = None
