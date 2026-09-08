"""SQLAlchemy models — imported so Alembic autogenerate sees the full schema."""

from app.models.activity import ActivityEntry
from app.models.ai_conversation import AIConversation
from app.models.ai_insight import AIInsight
from app.models.ai_message import AIMessage
from app.models.audit_log import AuditLog
from app.models.enums import (
    DataSource,
    FamilyHistoryCategory,
    GoalStatus,
    MedicalRecordCategory,
    NotificationType,
    PaymentStatus,
    PlanTier,
    SubscriptionStatus,
)
from app.models.family_history import FamilyHistory
from app.models.goal import HealthGoal
from app.models.health_metric import HealthMetric
from app.models.medical_record import MedicalRecord
from app.models.notification import Notification
from app.models.nutrition import NutritionEntry
from app.models.payment import Payment, PaymentEvent
from app.models.profile import HealthProfile
from app.models.report import HealthReport
from app.models.sleep import SleepEntry
from app.models.subscription import Subscription
from app.models.user import User
from app.models.wearable import WearableData
from app.models.wearable_connection import WearableConnection

__all__ = [
    "ActivityEntry",
    "AIConversation",
    "AIInsight",
    "AIMessage",
    "AuditLog",
    "DataSource",
    "FamilyHistory",
    "FamilyHistoryCategory",
    "GoalStatus",
    "HealthGoal",
    "HealthMetric",
    "HealthProfile",
    "HealthReport",
    "MedicalRecord",
    "MedicalRecordCategory",
    "Notification",
    "NotificationType",
    "NutritionEntry",
    "Payment",
    "PaymentEvent",
    "PaymentStatus",
    "PlanTier",
    "SleepEntry",
    "Subscription",
    "SubscriptionStatus",
    "User",
    "WearableData",
    "WearableConnection",
]
