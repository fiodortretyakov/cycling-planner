from __future__ import annotations

from typing import Any, Callable, Dict

from src.tools.routes import get_route
from src.tools.accommodation import find_accommodation
from src.tools.weather import get_weather
from src.tools.elevation import get_elevation_profile
from src.tools.poi import get_points_of_interest
from src.tools.visa import check_visa_requirements
from src.tools.budget import estimate_budget


ToolFunction = Callable[..., Any]


def get_available_tools() -> Dict[str, ToolFunction]:
    return {
        "get_route": get_route,
        "find_accommodation": find_accommodation,
        "get_weather": get_weather,
        "get_elevation_profile": get_elevation_profile,
        "get_points_of_interest": get_points_of_interest,
        "check_visa_requirements": check_visa_requirements,
        "estimate_budget": estimate_budget,
    }
