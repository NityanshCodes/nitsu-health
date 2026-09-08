"""Initial schema — full NITSU Health data model.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-09-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
        sa.Column("date_of_birth", sa.DateTime(), nullable=True),
        sa.Column("gender", sa.String(50), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column("timezone", sa.String(100), nullable=True),
        sa.Column("profile_picture", sa.String(255), nullable=True),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("onboarding_completed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("last_login", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "health_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("height_cm", sa.Float(), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("blood_type", sa.String(10), nullable=True),
        sa.Column("medical_conditions", sa.String(500), nullable=True),
        sa.Column("allergies", sa.Text(), nullable=True),
        sa.Column("medications", sa.Text(), nullable=True),
        sa.Column("lifestyle", sa.Text(), nullable=True),
        sa.Column("health_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_health_profiles_id", "health_profiles", ["id"])
    op.create_index("ix_health_profiles_user_id", "health_profiles", ["user_id"], unique=True)

    op.create_table(
        "family_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("relation", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_family_history_id", "family_history", ["id"])
    op.create_index("ix_family_history_user_id", "family_history", ["user_id"])

    op.create_table(
        "health_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("metric_type", sa.String(100), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(50), nullable=False),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_health_metrics_id", "health_metrics", ["id"])
    op.create_index("ix_health_metrics_user_id", "health_metrics", ["user_id"])
    op.create_index("ix_health_metrics_metric_type", "health_metrics", ["metric_type"])
    op.create_index("ix_health_metrics_recorded_at", "health_metrics", ["recorded_at"])

    op.create_table(
        "nutrition_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("meal_type", sa.String(50), nullable=False),
        sa.Column("calories", sa.Float(), nullable=False),
        sa.Column("protein_g", sa.Float(), nullable=False),
        sa.Column("carbs_g", sa.Float(), nullable=False),
        sa.Column("fats_g", sa.Float(), nullable=False),
        sa.Column("fiber_g", sa.Float(), nullable=False),
        sa.Column("water_ml", sa.Float(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("consumed_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_nutrition_entries_id", "nutrition_entries", ["id"])
    op.create_index("ix_nutrition_entries_user_id", "nutrition_entries", ["user_id"])

    op.create_table(
        "activity_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("activity_type", sa.String(100), nullable=False),
        sa.Column("steps", sa.Integer(), nullable=True),
        sa.Column("active_minutes", sa.Integer(), nullable=True),
        sa.Column("distance_km", sa.Float(), nullable=True),
        sa.Column("calories_burned", sa.Float(), nullable=True),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_activity_entries_id", "activity_entries", ["id"])
    op.create_index("ix_activity_entries_user_id", "activity_entries", ["user_id"])
    op.create_index("ix_activity_entries_recorded_at", "activity_entries", ["recorded_at"])

    op.create_table(
        "sleep_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=False),
        sa.Column("duration_minutes", sa.Float(), nullable=True),
        sa.Column("sleep_stages", sa.JSON(), nullable=True),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_sleep_entries_id", "sleep_entries", ["id"])
    op.create_index("ix_sleep_entries_user_id", "sleep_entries", ["user_id"])

    op.create_table(
        "wearable_connections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("access_token_enc", sa.Text(), nullable=True),
        sa.Column("refresh_token_enc", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(), nullable=True),
        sa.Column("scopes", sa.String(500), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_wearable_connections_id", "wearable_connections", ["id"])
    op.create_index("ix_wearable_connections_user_id", "wearable_connections", ["user_id"])

    op.create_table(
        "wearable_data",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("metric_type", sa.String(50), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(50), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_wearable_data_id", "wearable_data", ["id"])
    op.create_index("ix_wearable_data_user_id", "wearable_data", ["user_id"])

    op.create_table(
        "medical_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("file_path", sa.String(500), nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("recorded_at", sa.DateTime(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_medical_records_id", "medical_records", ["id"])
    op.create_index("ix_medical_records_user_id", "medical_records", ["user_id"])

    op.create_table(
        "health_goals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("goal_type", sa.String(100), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("target_value", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("progress_value", sa.Float(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_health_goals_id", "health_goals", ["id"])
    op.create_index("ix_health_goals_user_id", "health_goals", ["user_id"])

    op.create_table(
        "health_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("report_data", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("generated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_health_reports_id", "health_reports", ["id"])
    op.create_index("ix_health_reports_user_id", "health_reports", ["user_id"])

    op.create_table(
        "ai_conversations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("model_used", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_ai_conversations_id", "ai_conversations", ["id"])
    op.create_index("ix_ai_conversations_user_id", "ai_conversations", ["user_id"])

    op.create_table(
        "ai_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("ai_conversations.id"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("context_used", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_ai_messages_id", "ai_messages", ["id"])
    op.create_index("ix_ai_messages_conversation_id", "ai_messages", ["conversation_id"])

    op.create_table(
        "ai_insights",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("insight_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("source_data", sa.JSON(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("next_step", sa.Text(), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("generated_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_ai_insights_id", "ai_insights", ["id"])
    op.create_index("ix_ai_insights_user_id", "ai_insights", ["user_id"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", sa.String(30), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("link", sa.String(500), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_notifications_id", "notifications", ["id"])
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("plan", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("provider", sa.String(50), nullable=True),
        sa.Column("provider_subscription_id", sa.String(255), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_subscriptions_id", "subscriptions", ["id"])
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"], unique=True)

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("order_id", sa.String(100), nullable=False),
        sa.Column("provider_order_id", sa.String(255), nullable=True),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("provider", sa.String(50), nullable=True),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_payments_id", "payments", ["id"])
    op.create_index("ix_payments_user_id", "payments", ["user_id"])
    op.create_index("ix_payments_order_id", "payments", ["order_id"], unique=True)
    op.create_index("ix_payments_provider_order_id", "payments", ["provider_order_id"])

    op.create_table(
        "payment_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("payment_id", sa.Integer(), sa.ForeignKey("payments.id"), nullable=True),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("idempotency_key", sa.String(255), nullable=False),
        sa.Column("payload", sa.Text(), nullable=True),
        sa.Column("processed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_payment_events_id", "payment_events", ["id"])
    op.create_index("ix_payment_events_payment_id", "payment_events", ["payment_id"])
    op.create_index("ix_payment_events_idempotency_key", "payment_events", ["idempotency_key"], unique=True)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=True),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_audit_logs_id", "audit_logs", ["id"])
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])


def downgrade() -> None:
    op.drop_index("ix_audit_logs_action", table_name="audit_logs")
    op.drop_index("ix_audit_logs_user_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_id", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_payment_events_idempotency_key", table_name="payment_events")
    op.drop_index("ix_payment_events_payment_id", table_name="payment_events")
    op.drop_index("ix_payment_events_id", table_name="payment_events")
    op.drop_table("payment_events")

    op.drop_index("ix_payments_provider_order_id", table_name="payments")
    op.drop_index("ix_payments_order_id", table_name="payments")
    op.drop_index("ix_payments_user_id", table_name="payments")
    op.drop_index("ix_payments_id", table_name="payments")
    op.drop_table("payments")

    op.drop_index("ix_subscriptions_user_id", table_name="subscriptions")
    op.drop_index("ix_subscriptions_id", table_name="subscriptions")
    op.drop_table("subscriptions")

    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_index("ix_notifications_id", table_name="notifications")
    op.drop_table("notifications")

    op.drop_index("ix_ai_insights_user_id", table_name="ai_insights")
    op.drop_index("ix_ai_insights_id", table_name="ai_insights")
    op.drop_table("ai_insights")

    op.drop_index("ix_ai_messages_conversation_id", table_name="ai_messages")
    op.drop_index("ix_ai_messages_id", table_name="ai_messages")
    op.drop_table("ai_messages")

    op.drop_index("ix_ai_conversations_user_id", table_name="ai_conversations")
    op.drop_index("ix_ai_conversations_id", table_name="ai_conversations")
    op.drop_table("ai_conversations")

    op.drop_index("ix_health_reports_user_id", table_name="health_reports")
    op.drop_index("ix_health_reports_id", table_name="health_reports")
    op.drop_table("health_reports")

    op.drop_index("ix_health_goals_user_id", table_name="health_goals")
    op.drop_index("ix_health_goals_id", table_name="health_goals")
    op.drop_table("health_goals")

    op.drop_index("ix_medical_records_user_id", table_name="medical_records")
    op.drop_index("ix_medical_records_id", table_name="medical_records")
    op.drop_table("medical_records")

    op.drop_index("ix_wearable_data_user_id", table_name="wearable_data")
    op.drop_index("ix_wearable_data_id", table_name="wearable_data")
    op.drop_table("wearable_data")

    op.drop_index("ix_wearable_connections_user_id", table_name="wearable_connections")
    op.drop_index("ix_wearable_connections_id", table_name="wearable_connections")
    op.drop_table("wearable_connections")

    op.drop_index("ix_sleep_entries_user_id", table_name="sleep_entries")
    op.drop_index("ix_sleep_entries_id", table_name="sleep_entries")
    op.drop_table("sleep_entries")

    op.drop_index("ix_activity_entries_recorded_at", table_name="activity_entries")
    op.drop_index("ix_activity_entries_user_id", table_name="activity_entries")
    op.drop_index("ix_activity_entries_id", table_name="activity_entries")
    op.drop_table("activity_entries")

    op.drop_index("ix_nutrition_entries_user_id", table_name="nutrition_entries")
    op.drop_index("ix_nutrition_entries_id", table_name="nutrition_entries")
    op.drop_table("nutrition_entries")

    op.drop_index("ix_health_metrics_recorded_at", table_name="health_metrics")
    op.drop_index("ix_health_metrics_metric_type", table_name="health_metrics")
    op.drop_index("ix_health_metrics_user_id", table_name="health_metrics")
    op.drop_index("ix_health_metrics_id", table_name="health_metrics")
    op.drop_table("health_metrics")

    op.drop_index("ix_family_history_user_id", table_name="family_history")
    op.drop_index("ix_family_history_id", table_name="family_history")
    op.drop_table("family_history")

    op.drop_index("ix_health_profiles_user_id", table_name="health_profiles")
    op.drop_index("ix_health_profiles_id", table_name="health_profiles")
    op.drop_table("health_profiles")

    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
