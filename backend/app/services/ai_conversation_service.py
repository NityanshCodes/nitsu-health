"""AI conversation history management."""

from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.ai_conversation import AIConversation
from app.models.ai_message import AIMessage
from app.models.user import User


def list_conversations(
    db: Session,
    user: User,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[AIConversation], int]:
    query = db.query(AIConversation).filter(AIConversation.user_id == user.id)
    total = query.count()
    items = query.order_by(AIConversation.updated_at.desc()).limit(limit).offset(offset).all()
    return items, total


def get_conversation(
    db: Session,
    user: User,
    conversation_id: int,
) -> Optional[AIConversation]:
    return (
        db.query(AIConversation)
        .options(joinedload(AIConversation.messages))
        .filter(AIConversation.id == conversation_id, AIConversation.user_id == user.id)
        .first()
    )


def create_conversation(db: Session, user: User, title: Optional[str] = None) -> AIConversation:
    conv = AIConversation(user_id=user.id, title=title)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


def add_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str,
    context_used: Optional[dict] = None,
) -> AIMessage:
    msg = AIMessage(
        conversation_id=conversation_id,
        role=role,
        content=content,
        context_used=context_used,
    )
    db.add(msg)
    # Touch updated_at on parent
    conv = db.query(AIConversation).filter(AIConversation.id == conversation_id).first()
    if conv:
        from datetime import datetime
        conv.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(msg)
    return msg
