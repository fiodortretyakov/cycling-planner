from __future__ import annotations

from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()

from src.api.chat import router as chat_router

app = FastAPI(title="Cycling Trip Planner Agent")
app.include_router(chat_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
