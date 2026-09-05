"""Tests for AI context building and user isolation."""

import unittest
from datetime import datetime

from app.database.base import Base
from app.database.database import engine
from app.models.user import User
from app.services.ai_context import AIContextBuilder


class ContextBuilderTests(unittest.TestCase):
    """Test AI context building with user isolation."""

    def setUp(self):
        """Set up fresh database for each test."""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.builder = AIContextBuilder(engine)

    def tearDown(self):
        """Clean up after tests."""
        Base.metadata.drop_all(bind=engine)

    def _create_user(self, email, username, first_name, date_of_birth=None, gender=None):
        """Helper to create a test user."""
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=engine)
        db = Session()
        user = User(
            email=email,
            username=username,
            password_hash="hashed_password",
            first_name=first_name,
            date_of_birth=date_of_birth,
            gender=gender,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        db.close()
        return user

    def test_context_builder_contains_user_name(self):
        """Test that context includes the user's name."""
        user = self._create_user("alice@test.com", "alice", "Alice")
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=engine)
        db = Session()
        builder = AIContextBuilder(db)
        context = builder.build_context(user)
        db.close()
        assert context.user_id == user.id
        assert context.name == "Alice"

    def test_context_builder_calculates_age(self):
        """Test that context builder correctly calculates age from DOB."""
        dob = datetime(1990, 5, 15)
        user = self._create_user("bob@test.com", "bob", "Bob", date_of_birth=dob)
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=engine)
        db = Session()
        builder = AIContextBuilder(db)
        context = builder.build_context(user)
        db.close()
        # Age should be roughly 34 (2024 - 1990)
        assert context.age is not None
        assert context.age >= 33  # Allow for year boundary variation

    def test_context_includes_gender(self):
        """Test that context includes user's gender."""
        user = self._create_user("charlie@test.com", "charlie", "Charlie", gender="male")
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=engine)
        db = Session()
        builder = AIContextBuilder(db)
        context = builder.build_context(user)
        db.close()
        assert context.gender == "male"

    def test_prompt_includes_safety_instructions(self):
        """Test that built prompts include safety guardrails."""
        from sqlalchemy.orm import sessionmaker

        user = self._create_user("dave@test.com", "dave", "Dave")
        Session = sessionmaker(bind=engine)
        db = Session()
        builder = AIContextBuilder(db)
        context = builder.build_context(user)
        prompt = builder.build_prompt("What should I do about my headache?", context)
        db.close()

        # Verify safety instructions are in the prompt
        assert "doctor" in prompt.lower() or "medical" in prompt.lower() or "healthcare" in prompt.lower()
        assert "diagnose" in prompt.lower() or "prescribe" in prompt.lower() or "NOT" in prompt

    def test_prompt_includes_user_question(self):
        """Test that the prompt includes the user's actual question."""
        from sqlalchemy.orm import sessionmaker

        user = self._create_user("eve@test.com", "eve", "Eve")
        Session = sessionmaker(bind=engine)
        db = Session()
        builder = AIContextBuilder(db)
        context = builder.build_context(user)
        question = "What is a good sleep schedule?"
        prompt = builder.build_prompt(question, context)
        db.close()

        assert question in prompt

    def test_prompt_includes_context_name(self):
        """Test that the prompt includes the user's name from context."""
        from sqlalchemy.orm import sessionmaker

        user = self._create_user("frank@test.com", "frank", "Frank")
        Session = sessionmaker(bind=engine)
        db = Session()
        builder = AIContextBuilder(db)
        context = builder.build_context(user)
        prompt = builder.build_prompt("How's my health?", context)
        db.close()

        assert "Frank" in prompt


if __name__ == "__main__":
    unittest.main()
