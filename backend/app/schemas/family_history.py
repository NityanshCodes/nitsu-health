from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import FamilyHistoryCategory


class FamilyHistoryCreate(BaseModel):
    category: FamilyHistoryCategory
    relation: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = Field(default=None, max_length=2000)


class FamilyHistoryUpdate(BaseModel):
    category: Optional[FamilyHistoryCategory] = None
    relation: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = Field(default=None, max_length=2000)


class FamilyHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    category: str
    relation: Optional[str] = None
    notes: Optional[str] = None