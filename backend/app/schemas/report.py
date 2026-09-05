from pydantic import BaseModel, Field


class ReportResponse(BaseModel):
    user_id: int
    title: str = Field(..., min_length=1, max_length=255)
    status: str = Field(default="generated", max_length=50)
    summary: str = Field(..., min_length=1, max_length=5000)
