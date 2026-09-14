"""Shared enumeration values used across the data model.

Centralizing these keeps source semantics, goal status, plan tiers, etc.
consistent and avoids scattering magic strings throughout the codebase.
"""

import enum


class DataSource(str, enum.Enum):
    """Origin of a health data point.

    AI-generated values must never be represented as raw measured data.
    """

    MANUAL = "MANUAL"
    WEARABLE = "WEARABLE"
    IMPORTED = "IMPORTED"
    CALCULATED = "CALCULATED"
    AI_GENERATED = "AI_GENERATED"


class GoalStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class PlanTier(str, enum.Enum):
    FREE = "FREE"
    PREMIUM = "PREMIUM"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class PaymentStatus(str, enum.Enum):
    CREATED = "created"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"


class MedicalRecordCategory(str, enum.Enum):
    LAB = "lab"
    PRESCRIPTION = "prescription"
    VISIT = "visit"
    IMAGING = "imaging"
    VACCINATION = "vaccination"
    OTHER = "other"


class FamilyHistoryCategory(str, enum.Enum):
    DIABETES = "diabetes"
    HEART_DISEASE = "heart_disease"
    HYPERTENSION = "hypertension"
    CANCER = "cancer"
    STROKE = "stroke"
    MENTAL_HEALTH = "mental_health"
    OTHER = "other"


class NotificationType(str, enum.Enum):
    GOAL = "goal"
    DATA_ENTRY = "data_entry"
    REPORT = "report"
    WEARABLE = "wearable"
    SUBSCRIPTION = "subscription"
    SYSTEM = "system"
