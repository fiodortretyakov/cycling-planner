from __future__ import annotations

from fastapi import APIRouter

from src.agent.orchestrator import ConversationMemory, handle_chat
from src.agent.schemas import ChatRequest, ChatResponse

router = APIRouter()
_memory = ConversationMemory()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return handle_chat(request, _memory)
