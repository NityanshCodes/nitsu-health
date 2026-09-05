from fastapi import FastAPI
from . import api
import os

app = FastAPI(title="NITSU AI Engine")

app.include_router(api.router, prefix="/ai")


@app.on_event("startup")
async def startup_event():
    print("AI Engine starting...")


@app.get("/health")
async def health():
    return {"status": "running", "service": "ai-engine"}
