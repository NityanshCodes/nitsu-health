"""Sleep tracking."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database.base import Base
from app.models.enums import DataSource


class SleepEntry(Base):
    """A single sleep session.

    Sleep stages are only meaningful when supplied by a wearable; the
    `source` field keeps wearable-derived data clearly identified.
    """

    __tablename__ = "sleep_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration_minutes: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sleep_stages: Mapped[Optional[dict]] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=True)
    source: Mapped[str] = mapped_column(String(20), default=DataSource.MANUAL.value, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="sleep_entries")
