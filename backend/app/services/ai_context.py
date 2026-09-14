"""AI context builder for gathering user's health data safely."""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.activity import ActivityEntry
from app.models.goal import HealthGoal
from app.models.health_metric import HealthMetric
from app.models.medical_record import MedicalRecord
from app.models.nutrition import NutritionEntry
from app.models.profile import HealthProfile
from app.models.sleep import SleepEntry
from app.models.user import User
from app.schemas.ai import AIContextSummary


class AIContextBuilder:
    """Builds context for AI requests by gathering user's health data.

    Only fetches data belonging to the authenticated user.
    Never includes secrets or other users' data.
    """

    def __init__(self, db: Session):
        self.db = db

    def build_context(self, user: User) -> AIContextSummary:
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
        if not date_of_birth:
            return None
        today = datetime.utcnow()
        return today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))

    def _get_recent_vitals(self, user_id: int) -> Optional[Dict[str, Any]]:
        week_ago = datetime.utcnow() - timedelta(days=7)
        metrics = (
            self.db.query(HealthMetric)
            .filter(HealthMetric.user_id == user_id, HealthMetric.recorded_at >= week_ago)
            .order_by(HealthMetric.recorded_at.desc())
            .limit(10)
            .all()
        )
        if not metrics:
            return None
        vitals: Dict[str, Any] = {}
        for m in metrics:
            key = m.metric_type
            if key not in vitals:
                vitals[key] = {"value": m.value, "unit": m.unit, "recorded_at": str(m.recorded_at)}
        return vitals

    def _get_nutrition_summary(self, user_id: int) -> Optional[Dict[str, Any]]:
        today_start = datetime.combine(datetime.utcnow().date(), datetime.min.time())
        today_end = datetime.combine(datetime.utcnow().date(), datetime.max.time())
        entries = (
            self.db.query(NutritionEntry)
            .filter(
                NutritionEntry.user_id == user_id,
                NutritionEntry.consumed_at >= today_start,
                NutritionEntry.consumed_at <= today_end,
            )
            .all()
        )
        if not entries:
            return None
        return {
            "entries_today": len(entries),
            "calories": round(sum(e.calories for e in entries), 1),
            "protein_g": round(sum(e.protein_g for e in entries), 1),
            "carbs_g": round(sum(e.carbs_g for e in entries), 1),
            "fats_g": round(sum(e.fats_g for e in entries), 1),
        }

    def _get_health_goals(self, user_id: int) -> Optional[list]:
        goals = (
            self.db.query(HealthGoal)
            .filter(HealthGoal.user_id == user_id, HealthGoal.status == "active")
            .limit(5)
            .all()
        )
        if not goals:
            return None
        return [
            {
                "title": g.title,
                "target": f"{g.target_value} {g.unit}",
                "progress": f"{g.progress_value} {g.unit}",
            }
            for g in goals
        ]

    def _get_medical_notes_summary(self, user_id: int) -> Optional[str]:
        # Health profile
        profile = self.db.query(HealthProfile).filter(HealthProfile.user_id == user_id).first()
        parts = []
        if profile:
            if profile.medical_conditions:
                parts.append(f"Conditions: {profile.medical_conditions}")
            if profile.allergies:
                parts.append(f"Allergies: {profile.allergies}")
            if profile.medications:
                parts.append(f"Medications: {profile.medications}")

        # Recent medical records
        recent_records = (
            self.db.query(MedicalRecord)
            .filter(MedicalRecord.user_id == user_id)
            .order_by(MedicalRecord.created_at.desc())
            .limit(3)
            .all()
        )
        for r in recent_records:
            parts.append(f"Record: {r.title} ({r.category})")

        return "; ".join(parts) if parts else None

    def build_prompt(self, question: str, context: AIContextSummary) -> str:
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
        if context.medical_notes:
            context_part += f"Medical Notes: {context.medical_notes}\n"

        safety_instructions = (
            "IMPORTANT: You are a health information assistant, not a doctor.\n"
            "- Do NOT diagnose diseases or medical conditions.\n"
            "- Do NOT prescribe medication or recommend changing medications.\n"
            "- Do NOT claim to have performed medical tests.\n"
            "- Use cautious language like 'Your data shows...', 'This may warrant discussion with a healthcare professional'.\n"
            "- If the user asks for medical advice, recommend they consult a qualified healthcare professional.\n"
        )

        return (
            f"{safety_instructions}\n"
            f"User Context:\n{context_part}\n"
            f"User Question: {question}\n"
            f"Provide a helpful, cautious response based on the context and question."
        )
