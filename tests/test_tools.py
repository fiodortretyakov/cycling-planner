from src.tools.routes import get_route, RouteRequest
from src.tools.accommodation import find_accommodation, AccommodationRequest
from src.tools.weather import get_weather, WeatherRequest
from src.tools.elevation import get_elevation_profile, ElevationRequest


def test_route_returns_result():
    req = RouteRequest(origin="Amsterdam", destination="Copenhagen", preferred_daily_km=100)
    result = get_route(req)
    assert result.total_distance_km > 0
    assert result.waypoints


def test_accommodation_returns_option():
    req = AccommodationRequest(location="Hamburg", preference="camping")
    options = find_accommodation(req)
    assert options
    assert options[0].location.lower() == "hamburg"


def test_weather_mock():
    req = WeatherRequest(location="Amsterdam", month="June")
    result = get_weather(req)
    assert result.avg_temp_c > 0


def test_elevation_profile():
    req = ElevationRequest(origin="Amsterdam", destination="Copenhagen")
    result = get_elevation_profile(req)
    assert result.total_elevation_gain_m > 0
