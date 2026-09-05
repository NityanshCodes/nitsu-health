import os
from typing import Any, Dict, List, Optional

import httpx

AI_ENGINE_URL = os.getenv("AI_ENGINE_URL", "http://localhost:8001/ai")


class AIService:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or AI_ENGINE_URL).rstrip("/")

    async def chat(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat",
                json={"message": message, "session_id": session_id},
            )
            response.raise_for_status()
            return response.json()

    async def ingest(self, documents: List[Dict[str, str]]) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{self.base_url}/ingest", json=documents)
            response.raise_for_status()
            return response.json()

    async def search(self, query: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{self.base_url}/search", json={"q": query})
            response.raise_for_status()
            return response.json()

    async def summarize_health(self, user_profile: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        prompt = (
            "Create a concise health summary based on the profile and metrics. "
            f"Profile: {user_profile}. Metrics: {metrics}. "
            "Respond with a short paragraph and 3 bullet insights."
        )
        result = await self.chat(prompt, session_id="summary")
        return {"summary": result.get("reply", "No summary available")}


ai_service = AIService()
