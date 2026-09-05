from pydantic import BaseModel


class AppSettings(BaseModel):
    app_name: str = "NITSU Health"
    env: str = "development"
    debug: bool = True
    api_version: str = "v1"
    ai_engine_url: str = "http://localhost:8001/ai"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:4173"]


settings = AppSettings()
