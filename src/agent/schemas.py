from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


Role = Literal["user", "assistant", "system", "tool"]


class ChatMessage(BaseModel):
    role: Role
    content: str


class DayPlan(BaseModel):
    day: int
    start: str
    end: str
    distance_km: float
    accommodation: str
    weather: str
    elevation: str
    notes: str | None = None


class ChatRequest(BaseModel):
    session_id: str | None = Field(None, description="Client-provided session identifier")
    message: str
    preferences: dict | None = Field(default_factory=dict)


class ChatResponse(BaseModel):
    session_id: str
    messages: list[ChatMessage]
    day_plan: list[DayPlan] | None = None
    clarifying_questions: list[str] | None = None
    status: Literal["ok", "needs_clarification"] = "ok"
