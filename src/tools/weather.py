from __future__ import annotations

import httpx
from pydantic import BaseModel


class WeatherRequest(BaseModel):
    location: str
    month: str


class WeatherResult(BaseModel):
    location: str
    month: str
    avg_temp_c: float
    precipitation_mm: float
    notes: str


MOCK_WEATHER = {
    ("copenhagen", "june"): WeatherResult(
        location="Copenhagen",
        month="June",
        avg_temp_c=17.0,
        precipitation_mm=55.0,
        notes="Mild temps, light coastal breeze",
    ),
    ("amsterdam", "june"): WeatherResult(
        location="Amsterdam",
        month="June",
        avg_temp_c=16.0,
        precipitation_mm=70.0,
        notes="Chance of showers, pack a light rain jacket",
    ),
}


def get_weather(request: WeatherRequest) -> WeatherResult:
    """
    Get weather data using Open-Meteo API (free, no API key required).
    Falls back to mock data if API is unavailable.
    """
    try:
        # First geocode the location
        coords = _geocode_location(request.location)
        if coords:
            weather_data = _fetch_weather_data(coords, request.month)
            if weather_data:
                return weather_data
    except Exception:
        pass
    
    # Fallback to mock data
    key = (request.location.lower().strip(), request.month.lower().strip())
    if key in MOCK_WEATHER:
        return MOCK_WEATHER[key]
    
    return WeatherResult(
        location=request.location.title(),
        month=request.month.title(),
        avg_temp_c=18.0,
        precipitation_mm=60.0,
        notes="Typical temperate summer conditions",
    )


def _geocode_location(location: str) -> tuple[float, float] | None:
    """Geocode location using Nominatim API."""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": location,
            "format": "json",
            "limit": 1
        }
        headers = {"User-Agent": "CyclingPlanner/1.0"}
        
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, params=params, headers=headers)
            response.raise_for_status()
            results = response.json()
            
            if results:
                return (float(results[0]["lat"]), float(results[0]["lon"]))
    except Exception:
        pass
    return None


def _fetch_weather_data(coords: tuple[float, float], month: str) -> WeatherResult | None:
    """Fetch historical weather data from Open-Meteo API."""
    lat, lon = coords
    
    # Map month to a representative date (use 2023 as reference year)
    month_to_num = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12
    }
    
    month_num = month_to_num.get(month.lower())
    if not month_num:
        return None
    
    # Use climate API for historical averages
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    # Get data for the month in 2023
    start_date = f"2023-{month_num:02d}-01"
    if month_num == 12:
        end_date = "2023-12-31"
    else:
        import calendar
        last_day = calendar.monthrange(2023, month_num)[1]
        end_date = f"2023-{month_num:02d}-{last_day:02d}"
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_mean,precipitation_sum",
        "timezone": "auto"
    }
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            daily = data.get("daily", {})
            temps = daily.get("temperature_2m_mean", [])
            precip = daily.get("precipitation_sum", [])
            
            if temps and precip:
                avg_temp = sum(temps) / len(temps)
                total_precip = sum(precip)
                
                # Create descriptive notes
                notes = []
                if avg_temp < 10:
                    notes.append("Cool temperatures")
                elif avg_temp > 25:
                    notes.append("Warm temperatures")
                else:
                    notes.append("Mild temperatures")
                
                if total_precip > 100:
                    notes.append("wet season, bring rain gear")
                elif total_precip < 30:
                    notes.append("dry season")
                else:
                    notes.append("moderate rainfall")
                
                return WeatherResult(
                    location=request.location.title(),
                    month=request.month.title(),
                    avg_temp_c=round(avg_temp, 1),
                    precipitation_mm=round(total_precip, 1),
                    notes=", ".join(notes)
                )
    except Exception:
        pass
    
    return None
