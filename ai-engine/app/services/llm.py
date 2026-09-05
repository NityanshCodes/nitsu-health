import os
from typing import Optional

try:
    import httpx
except Exception:  # pragma: no cover - optional network client
    httpx = None


class LLMService:
    """Minimal LLM wrapper used by the AI engine.

    If `OPENAI_API_KEY` is present it will call OpenAI's chat endpoint via HTTP.
    Otherwise it returns a deterministic echo fallback for local development.
    """

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._client = httpx.AsyncClient() if httpx is not None else None

    async def generate(self, prompt: str, session_id: Optional[str] = None) -> str:
        if self.api_key and self._client is not None:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 512,
            }
            resp = await self._client.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()

        # Fallback deterministic response for offline/dev
        return f"Echo: {prompt}"
