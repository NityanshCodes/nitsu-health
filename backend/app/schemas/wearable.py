from pydantic import BaseModel, Field


class WearableDataResponse(BaseModel):
    user_id: int
    status: str = Field(default="connected", max_length=50)
    provider: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., min_length=1, max_length=500)
