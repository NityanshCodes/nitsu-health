from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings


def _make_engine(url: str):
    """Create an engine; for in-memory SQLite use a shared StaticPool so that
    the TestClient and direct-DB fixture calls share the same database."""
    if url.startswith("sqlite:") and ("mode=memory" in url or url == "sqlite://"):
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    return create_engine(url, pool_pre_ping=True)


engine = _make_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
