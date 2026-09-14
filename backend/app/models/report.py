"""Health / wellness reports."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database.base import Base


class HealthReport(Base):
    """A stored wellness report.

    `report_data` holds the structured report sections. Reports are stored
    for historical viewing and are never presented as medical diagnoses.
    """

    __tablename__ = "health_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    report_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    report_type: Mapped[str] = mapped_column(String(50), default="wellness", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="generated", nullable=False)
    generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="health_reports")
