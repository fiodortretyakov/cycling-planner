from __future__ import annotations

from typing import List, Literal, Optional
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
    notes: Optional[str] = None


class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Client-provided session identifier")
    message: str
    preferences: Optional[dict] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    day_plan: Optional[List[DayPlan]] = None
    clarifying_questions: Optional[List[str]] = None
    status: Literal["ok", "needs_clarification"] = "ok"
