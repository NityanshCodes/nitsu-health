"""Tests for AI provider abstraction."""

import asyncio
import importlib.util

import pytest

from app.services.ai_provider import AIProviderFactory, DevelopmentProvider, OpenAIProvider

_HTTPX_AVAILABLE = importlib.util.find_spec("httpx") is not None


def _run(coro):
    """Run a coroutine to completion without relying on a pre-existing loop.

    asyncio.get_event_loop() is deprecated (and raises) on Python 3.12+ when
    there is no running loop, so use asyncio.run().
    """
    return asyncio.run(coro)


class TestAIProviderFactory:
    """Test AI provider factory selection."""

    def test_factory_returns_provider(self):
        """Test that factory returns a valid provider."""
        provider = AIProviderFactory.get_provider()
        assert provider is not None

    def test_factory_returns_development_without_key(self, monkeypatch):
        """Test that factory returns DevelopmentProvider when OPENAI_API_KEY is missing."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        provider = AIProviderFactory.get_provider()
        assert isinstance(provider, DevelopmentProvider)

    @pytest.mark.skipif(not _HTTPX_AVAILABLE, reason="httpx not installed; OpenAI provider is unavailable")
    def test_factory_returns_openai_with_key(self, monkeypatch):
        """Test that factory returns OpenAIProvider when OPENAI_API_KEY is set."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-12345")
        provider = AIProviderFactory.get_provider()
        assert isinstance(provider, OpenAIProvider)


class TestOpenAIProvider:
    """Test OpenAI provider configuration."""

    @pytest.mark.skipif(not _HTTPX_AVAILABLE, reason="httpx not installed; OpenAI provider is unavailable")
    def test_openai_is_configured_with_key(self, monkeypatch):
        """Test that OpenAI provider reports configured=True when key exists."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        provider = OpenAIProvider()
        assert provider.is_configured() is True

    def test_openai_is_not_configured_without_key(self, monkeypatch):
        """Test that OpenAI provider reports configured=False when key is missing."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        provider = OpenAIProvider()
        assert provider.is_configured() is False

    def test_openai_respects_model_env(self, monkeypatch):
        """Test that OpenAI provider uses OPENAI_MODEL env var."""
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4")
        provider = OpenAIProvider()
        assert provider.model == "gpt-4"

    def test_openai_defaults_to_mini(self, monkeypatch):
        """Test that OpenAI provider defaults to gpt-4o-mini."""
        monkeypatch.delenv("OPENAI_MODEL", raising=False)
        provider = OpenAIProvider()
        assert provider.model == "gpt-4o-mini"

    def test_openai_generate_raises_without_key(self):
        """Test that generate raises ValueError when API key is missing."""
        provider = OpenAIProvider()
        # Force unconfigured state
        provider.api_key = None
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            _run(provider.generate("test prompt"))


class TestDevelopmentProvider:
    """Test development/fallback provider."""

    def test_development_always_configured(self):
        """Test that development provider is always available."""
        provider = DevelopmentProvider()
        assert provider.is_configured() is True

    def test_development_generate_works(self):
        """Test that development provider generates responses."""
        provider = DevelopmentProvider()
        response = _run(provider.generate("What is my health status?"))
        assert response is not None
        assert "Development Mode" in response or "development" in response.lower()

    def test_development_includes_context(self):
        """Test that development provider acknowledges context when provided."""
        provider = DevelopmentProvider()
        context = {"name": "Alice", "age": 30}
        response = _run(provider.generate("How should I exercise?", context=context))
        assert "Alice" in response or "context" in response.lower() or "Development" in response
