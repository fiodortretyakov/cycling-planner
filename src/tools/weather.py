from __future__ import annotations

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
