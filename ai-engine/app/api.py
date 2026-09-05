from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .services.embedding import EmbeddingService
from .services.llm import LLMService
from .services.vectorstore import InMemoryVectorStore

router = APIRouter()
llm = LLMService()
emb = EmbeddingService()
vstore = InMemoryVectorStore()


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        reply = await llm.generate(req.message, session_id=req.session_id)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class IngestDoc(BaseModel):
    id: str
    text: str


@router.post("/ingest")
async def ingest(docs: List[IngestDoc]):
    """Ingest documents into the in-memory vector store."""
    try:
        texts = [d.text for d in docs]
        vectors = emb.embed(texts)
        items = [(d.id, d.text, v) for d, v in zip(docs, vectors)]
        vstore.add_documents(items)
        return {"ingested": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search(query: dict):
    q = query.get("q") or query.get("query")
    if not q:
        raise HTTPException(status_code=400, detail="query missing")
    qvec = emb.embed([q])[0]
    results = vstore.search(qvec, top_k=5)
    return {"results": results}
