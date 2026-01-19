from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


class RouteWaypoint(BaseModel):
    name: str
    distance_from_start_km: float


class RouteRequest(BaseModel):
    origin: str
    destination: str
    preferred_daily_km: Optional[float] = None


class RouteResult(BaseModel):
    origin: str
    destination: str
    total_distance_km: float
    estimated_days: int
    waypoints: List[RouteWaypoint]


MOCK_ROUTES = {
    ("amsterdam", "copenhagen"): RouteResult(
        origin="Amsterdam",
        destination="Copenhagen",
        total_distance_km=780.0,
        estimated_days=8,
        waypoints=[
            RouteWaypoint(name="Almere", distance_from_start_km=30),
            RouteWaypoint(name="Lelystad", distance_from_start_km=55),
            RouteWaypoint(name="Zwolle", distance_from_start_km=120),
            RouteWaypoint(name="Meppel", distance_from_start_km=140),
            RouteWaypoint(name="Groningen", distance_from_start_km=185),
            RouteWaypoint(name="Leer", distance_from_start_km=225),
            RouteWaypoint(name="Oldenburg", distance_from_start_km=310),
            RouteWaypoint(name="Bremen", distance_from_start_km=380),
            RouteWaypoint(name="Hamburg", distance_from_start_km=480),
            RouteWaypoint(name="Lubeck", distance_from_start_km=575),
            RouteWaypoint(name="Puttgarden", distance_from_start_km=670),
            RouteWaypoint(name="Rodby", distance_from_start_km=715),
            RouteWaypoint(name="Copenhagen", distance_from_start_km=780),
        ],
    )
}


def get_route(request: RouteRequest) -> RouteResult:
    key = (request.origin.lower().strip(), request.destination.lower().strip())
    if key in MOCK_ROUTES:
        route = MOCK_ROUTES[key]
    else:
        # Simple fall-back mock: 600km with evenly spaced waypoints
        total_distance = 600.0
        segments = [
            RouteWaypoint(name=f"Waypoint {i}", distance_from_start_km=i * 100.0)
            for i in range(1, 6)
        ]
        segments.append(RouteWaypoint(name=request.destination.title(), distance_from_start_km=total_distance))
        route = RouteResult(
            origin=request.origin.title(),
            destination=request.destination.title(),
            total_distance_km=total_distance,
            estimated_days=max(1, int(total_distance / (request.preferred_daily_km or 100))),
            waypoints=segments,
        )
    return route
