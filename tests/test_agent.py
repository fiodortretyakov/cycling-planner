from src.agent.orchestrator import ConversationMemory, handle_chat
from src.agent.schemas import ChatRequest


def test_handle_chat_builds_plan():
    memory = ConversationMemory()
    request = ChatRequest(message="I want to cycle from Amsterdam to Copenhagen in June around 100km per day and a hostel every 4th night.")
    response = handle_chat(request, memory)
    assert response.status == "ok"
    assert response.day_plan
    assert response.day_plan[0].end
