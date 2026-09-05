import pytest
from fastapi import status
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/health")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json().get("service") == "ai-engine"


@pytest.mark.asyncio
async def test_ingest_and_search():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        docs = [{"id": "d1", "text": "The quick brown fox"}, {"id": "d2", "text": "Jumped over the lazy dog"}]
        resp = await ac.post("/ai/ingest", json=docs)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json().get("ingested") == 2

        resp = await ac.post("/ai/search", json={"q": "quick fox"})
        assert resp.status_code == status.HTTP_200_OK
        results = resp.json().get("results")
        assert isinstance(results, list)
        assert len(results) > 0
