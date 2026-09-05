"""AI Provider abstraction for pluggable LLM backends."""

import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import httpx


class AIProvider(ABC):
    """Base class for AI providers."""

    @abstractmethod
    async def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response from the AI provider.

        Args:
            prompt: The user's question or prompt
            context: Optional context dict with health data

        Returns:
            The generated response text

        Raises:
            ValueError: If required credentials are missing
            httpx.HTTPError: If the provider is unreachable
        """
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the provider has necessary credentials configured."""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI provider using their chat API."""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    def is_configured(self) -> bool:
        """Check if OpenAI API key is set."""
        return bool(self.api_key)

    async def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate response using OpenAI API."""
        if not self.is_configured():
            raise ValueError("OPENAI_API_KEY is not configured")

        client = await self._get_client()

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024,
            "temperature": 0.7,
        }

        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            json=payload,
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()


class DevelopmentProvider(AIProvider):
    """Fallback provider for development that returns structured but deterministic responses."""

    def is_configured(self) -> bool:
        """Always available for development."""
        return True

    async def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a development response with awareness of context."""
        # Build a simple but useful response that shows context awareness
        context_str = ""
        if context:
            context_str = f"\n[Context: {context.get('name', 'User')} is {context.get('age', '?')} years old. "
            if context.get("recent_vitals"):
                vitals = context["recent_vitals"]
                context_str += f"Recent vitals: {json.dumps(vitals, indent=0).replace(chr(10), ' ')}. "
            context_str += "]"

        # Create a deterministic but helpful development response
        return (
            f"Development Mode Response: Your question about '{prompt[:50]}...' has been received. "
            f"{context_str} "
            f"This is a development/mock response. In production, this would be handled by the configured AI provider."
        )


class AIProviderFactory:
    """Factory for creating AI providers based on configuration."""

    @staticmethod
    def get_provider() -> AIProvider:
        """Get the appropriate AI provider based on environment configuration.

        Returns:
            An AIProvider instance (OpenAI if configured, otherwise Development)
        """
        openai_provider = OpenAIProvider()
        if openai_provider.is_configured():
            return openai_provider
        return DevelopmentProvider()
