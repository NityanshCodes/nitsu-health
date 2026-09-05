"""AI context builder for gathering user's health data safely."""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.ai import AIContextSummary


class AIContextBuilder:
    """Builds context for AI requests by gathering user's health data.

    Only fetches data belonging to the authenticated user.
    Calculates derived metrics to reduce unnecessary data.
    """

    def __init__(self, db: Session):
        self.db = db

    def build_context(self, user: User) -> AIContextSummary:
        """Build a sanitized health context for the authenticated user.

        Args:
            user: The authenticated User object

        Returns:
            AIContextSummary with only relevant, user-specific data
        """
        return AIContextSummary(
            user_id=user.id,
            name=user.first_name or user.username,
            age=self._calculate_age(user.date_of_birth) if user.date_of_birth else None,
            gender=user.gender,
            recent_vitals=self._get_recent_vitals(user.id),
            nutrition_summary=self._get_nutrition_summary(user.id),
            health_goals=self._get_health_goals(user.id),
            medical_notes=self._get_medical_notes_summary(user.id),
        )

    def _calculate_age(self, date_of_birth: datetime) -> Optional[int]:
        """Calculate age from date of birth."""
        if not date_of_birth:
            return None
        today = datetime.utcnow()
        return today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))

    def _get_recent_vitals(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get recent vital signs (if available in database).

        This is a placeholder. In production, fetch from wearables/health tracking models.
        """
        # TODO: Query wearable_data or vitals table when implemented
        # For now, return None to show we checked but have no data
        return None

    def _get_nutrition_summary(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get nutrition summary (if available in database).

        This is a placeholder. In production, summarize meals logged.
        """
        # TODO: Query nutrition/meal entries, calculate totals/averages
        return None

    def _get_health_goals(self, user_id: int) -> Optional[list]:
        """Get user's health goals (if available in database).

        This is a placeholder. In production, fetch from goals model.
        """
        # TODO: Query goals model
        return None

    def _get_medical_notes_summary(self, user_id: int) -> Optional[str]:
        """Get summary of recent medical records (if available).

        This is a placeholder. In production, summarize medical records.
        """
        # TODO: Query medical_records model, extract recent entries
        return None

    def build_prompt(self, question: str, context: AIContextSummary) -> str:
        """Build a complete prompt for the AI with context and safety instructions.

        Args:
            question: The user's question
            context: The health context

        Returns:
            A complete prompt with safety instructions
        """
        context_part = ""
        if context.name:
            context_part += f"User: {context.name}\n"
        if context.age:
            context_part += f"Age: {context.age}\n"
        if context.gender:
            context_part += f"Gender: {context.gender}\n"
        if context.recent_vitals:
            context_part += f"Recent Vitals: {context.recent_vitals}\n"
        if context.nutrition_summary:
            context_part += f"Nutrition Summary: {context.nutrition_summary}\n"
        if context.health_goals:
            context_part += f"Health Goals: {context.health_goals}\n"

        safety_instructions = (
            "IMPORTANT: You are a health information assistant, not a doctor.\n"
            "- Do NOT diagnose diseases or medical conditions.\n"
            "- Do NOT prescribe medication or recommend changing medications.\n"
            "- Do NOT claim to have performed medical tests.\n"
            "- Use cautious language like 'Your data shows...', 'This may warrant discussion with a healthcare professional'.\n"
            "- If the user asks for medical advice, recommend they consult a qualified healthcare professional.\n"
        )

        prompt = (
            f"{safety_instructions}\n"
            f"User Context:\n{context_part}\n"
            f"User Question: {question}\n"
            f"Provide a helpful, cautious response based on the context and question."
        )

        return prompt
