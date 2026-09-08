from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api import (
    activity as activity_router,
    admin as admin_router,
    ai as ai_router,
    analytics as analytics_router,
    auth as auth_router,
    dashboard as dashboard_router,
    goals as goals_router,
    health as health_router,
    medical_records as medical_records_router,
    notifications as notifications_router,
    nutrition as nutrition_router,
    payments as payments_router,
    profile as profile_router,
    reports as reports_router,
    search as search_router,
    sleep as sleep_router,
    subscription as subscription_router,
    users as users_router,
    wearables as wearables_router,
)
from app.core.config import settings
from app.database.base import Base
from app.database.database import engine, get_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Development convenience: in non-production environments create tables
    # automatically. Production schema is owned by Alembic migrations
    # (`alembic upgrade head`) and never auto-created here.
    if settings.environment != "production":
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(profile_router.router)
app.include_router(health_router.router)
app.include_router(nutrition_router.router)
app.include_router(activity_router.router)
app.include_router(sleep_router.router)
app.include_router(wearables_router.router)
app.include_router(goals_router.router)
app.include_router(reports_router.router)
app.include_router(dashboard_router.router)
app.include_router(analytics_router.router)
app.include_router(ai_router.router)
app.include_router(medical_records_router.router)
app.include_router(notifications_router.router)
app.include_router(search_router.router)
app.include_router(subscription_router.router)
app.include_router(payments_router.router)
app.include_router(admin_router.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "running", "service": "backend", "environment": settings.environment}


@app.get("/health/ready")
def readiness(db: Session = Depends(get_db)) -> dict:
    """Readiness probe — confirms DB connectivity."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
    return {
        "status": "ready" if db_status == "ok" else "degraded",
        "database": db_status,
    }