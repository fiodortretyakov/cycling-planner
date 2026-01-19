import pytest
from unittest.mock import patch, MagicMock
from src.tools.routes import get_route, RouteRequest
from src.tools.accommodation import find_accommodation, AccommodationRequest
from src.tools.weather import get_weather, WeatherRequest
from src.tools.elevation import get_elevation_profile, ElevationRequest


@patch('src.tools.routes.httpx.Client')
def test_route_returns_result(mock_client):
    """Test route returns result with mocked API calls."""
    # Mock the geocoding responses
    mock_response = MagicMock()
    mock_response.json.return_value = []  # Empty response to trigger fallback
    mock_response.raise_for_status = MagicMock()
    
    mock_http = MagicMock()
    mock_http.get.return_value = mock_response
    mock_http.post.return_value = mock_response
    mock_http.__enter__.return_value = mock_http
    mock_http.__exit__.return_value = None
    mock_client.return_value = mock_http
    
    req = RouteRequest(origin="Amsterdam", destination="Copenhagen", preferred_daily_km=100)
    result = get_route(req)
    assert result.total_distance_km > 0
    assert result.waypoints


@patch('src.tools.accommodation.httpx.Client')
def test_accommodation_returns_option(mock_client):
    """Test accommodation returns options with mocked API calls."""
    # Mock empty API response to trigger fallback to mock data
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = MagicMock()
    
    mock_http = MagicMock()
    mock_http.get.return_value = mock_response
    mock_http.post.return_value = mock_response
    mock_http.__enter__.return_value = mock_http
    mock_http.__exit__.return_value = None
    mock_client.return_value = mock_http
    
    req = AccommodationRequest(location="Hamburg", preference="camping")
    options = find_accommodation(req)
    assert options
    assert "hamburg" in options[0].location.lower()


@patch('src.tools.weather.httpx.Client')
def test_weather_mock(mock_client):
    """Test weather returns result with mocked API calls."""
    # Mock empty API response to trigger fallback
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = MagicMock()
    
    mock_http = MagicMock()
    mock_http.get.return_value = mock_response
    mock_http.__enter__.return_value = mock_http
    mock_http.__exit__.return_value = None
    mock_client.return_value = mock_http
    
    req = WeatherRequest(location="Amsterdam", month="June")
    result = get_weather(req)
    assert result.avg_temp_c > 0


@patch('src.tools.elevation.httpx.Client')
def test_elevation_profile(mock_client):
    """Test elevation returns result with mocked API calls."""
    # Mock empty API response to trigger fallback
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = MagicMock()
    
    mock_http = MagicMock()
    mock_http.get.return_value = mock_response
    mock_http.post.return_value = mock_response
    mock_http.__enter__.return_value = mock_http
    mock_http.__exit__.return_value = None
    mock_client.return_value = mock_http
    
    req = ElevationRequest(origin="Amsterdam", destination="Copenhagen")
    result = get_elevation_profile(req)
    assert result.total_elevation_gain_m > 0
