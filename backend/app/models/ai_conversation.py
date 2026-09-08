"""AI conversation sessions (owned per user)."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AIConversation(Base):
    """A user's conversation session with the AI assistant.

    Messages within a conversation are stored in AIMessage. All records are
    scoped to a user so one user can never access another's conversations.
    """

    __tablename__ = "ai_conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    model_used: Mapped[str] = mapped_column(String(100), default="gpt-4o-mini", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="ai_conversations")
    messages: Mapped[List["AIMessage"]] = relationship(
        "AIMessage", back_populates="conversation", cascade="all, delete-orphan"
    )
