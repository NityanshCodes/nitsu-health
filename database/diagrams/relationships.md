# Relationships Overview

- users 1..* profiles
- users 1..* appointments
- users 1..* medical_records
- users 1..* nutrition_logs
- users 1..* wearables
- users 1..* reports
- users 1..* notifications
- users 1..* sessions
- users 1..* tokens
- medical_records 1..* reports
- nutrition_logs 1..* meal_plans
- wearables 1..* predictions
- reports 1..* ai_conversations
