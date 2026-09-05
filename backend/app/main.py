from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ai as ai_router
from app.api import auth as auth_router
from app.api import dashboard as dashboard_router
from app.api import nutrition as nutrition_router
from app.api import reports as reports_router
from app.api import users as users_router
from app.api import wearable as wearable_router
from app.core.config import settings
from app.database.base import Base
from app.database.database import engine
from app.models import ai_chat as ai_chat_model
from app.models import user as user_model

app = FastAPI(title="NITSU Health API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(dashboard_router.router)
app.include_router(nutrition_router.router)
app.include_router(reports_router.router)
app.include_router(wearable_router.router)
app.include_router(ai_router.router)

Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "running", "service": "backend"}
