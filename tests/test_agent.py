from unittest.mock import patch, MagicMock
from src.agent.orchestrator import ConversationMemory, handle_chat
from src.agent.schemas import ChatRequest


@patch('src.tools.routes.httpx.Client')
@patch('src.tools.accommodation.httpx.Client')
@patch('src.tools.weather.httpx.Client')
@patch('src.tools.elevation.httpx.Client')
def test_handle_chat_builds_plan(mock_elev, mock_weather, mock_accom, mock_route):
    """Test chat handler builds plan with mocked API calls."""
    # Mock all HTTP clients to return empty responses (triggers fallbacks to mock data)
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = MagicMock()
    
    mock_http = MagicMock()
    mock_http.get.return_value = mock_response
    mock_http.post.return_value = mock_response
    mock_http.__enter__.return_value = mock_http
    mock_http.__exit__.return_value = None
    
    mock_route.return_value = mock_http
    mock_accom.return_value = mock_http
    mock_weather.return_value = mock_http
    mock_elev.return_value = mock_http
    
    memory = ConversationMemory()
    request = ChatRequest(message="I want to cycle from Amsterdam to Copenhagen in June around 100km per day and a hostel every 4th night.")
    response = handle_chat(request, memory)
    assert response.status == "ok"
    assert response.day_plan
    assert response.day_plan[0].end
