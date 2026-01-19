from __future__ import annotations

import os
import httpx
from pydantic import BaseModel


class RouteWaypoint(BaseModel):
    name: str
    distance_from_start_km: float


class RouteRequest(BaseModel):
    origin: str
    destination: str
    preferred_daily_km: float | None = None


class RouteResult(BaseModel):
    origin: str
    destination: str
    total_distance_km: float
    estimated_days: int
    waypoints: list[RouteWaypoint]


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
    """
    Get cycling route using OpenRouteService API.
    Falls back to Nominatim geocoding + distance calculation if ORS is unavailable.
    """
    ors_api_key = os.environ.get("OPENROUTESERVICE_API_KEY")
    
    # Try to geocode locations first
    origin_coords = _geocode_location(request.origin)
    dest_coords = _geocode_location(request.destination)
    
    if not origin_coords or not dest_coords:
        # Fall back to mock data
        return _get_mock_route(request)
    
    if ors_api_key:
        try:
            return _get_ors_route(request, origin_coords, dest_coords, ors_api_key)
        except Exception:
            pass
    
    # Fallback: calculate straight-line distance and create waypoints
    return _create_simple_route(request, origin_coords, dest_coords)


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
                return (float(results[0]["lon"]), float(results[0]["lat"]))
    except Exception:
        pass
    return None


def _get_ors_route(
    request: RouteRequest,
    origin_coords: tuple[float, float],
    dest_coords: tuple[float, float],
    api_key: str
) -> RouteResult:
    """Get route from OpenRouteService API."""
    url = "https://api.openrouteservice.org/v2/directions/cycling-regular"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "coordinates": [list(origin_coords), list(dest_coords)],
        "instructions": True,
        "elevation": True
    }
    
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        route = data["routes"][0]
        distance_km = route["summary"]["distance"] / 1000
        daily_km = request.preferred_daily_km or 100.0
        estimated_days = max(1, int(distance_km / daily_km))
        
        # Extract waypoints from route segments
        waypoints = []
        segments = route.get("segments", [])
        cumulative_distance = 0.0
        
        for segment in segments:
            for step in segment.get("steps", []):
                cumulative_distance += step["distance"] / 1000
                if step.get("name"):
                    waypoints.append(RouteWaypoint(
                        name=step["name"],
                        distance_from_start_km=round(cumulative_distance, 1)
                    ))
        
        # Ensure destination is included
        if not waypoints or waypoints[-1].distance_from_start_km < distance_km:
            waypoints.append(RouteWaypoint(
                name=request.destination.title(),
                distance_from_start_km=round(distance_km, 1)
            ))
        
        return RouteResult(
            origin=request.origin.title(),
            destination=request.destination.title(),
            total_distance_km=round(distance_km, 1),
            estimated_days=estimated_days,
            waypoints=waypoints[:20]  # Limit waypoints
        )


def _haversine_distance(coord1: tuple[float, float], coord2: tuple[float, float]) -> float:
    """Calculate distance between two coordinates in km using Haversine formula."""
    import math
    
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    
    R = 6371  # Earth radius in km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def _create_simple_route(
    request: RouteRequest,
    origin_coords: tuple[float, float],
    dest_coords: tuple[float, float]
) -> RouteResult:
    """Create a simple route with estimated waypoints."""
    distance_km = _haversine_distance(origin_coords, dest_coords)
    
    # Add 20% for realistic cycling distance (not straight line)
    distance_km = distance_km * 1.2
    
    daily_km = request.preferred_daily_km or 100.0
    estimated_days = max(1, int(distance_km / daily_km))
    
    # Create intermediate waypoints
    num_waypoints = min(10, estimated_days)
    waypoints = []
    
    for i in range(1, num_waypoints + 1):
        dist = (distance_km / num_waypoints) * i
        waypoints.append(RouteWaypoint(
            name=f"Waypoint {i}",
            distance_from_start_km=round(dist, 1)
        ))
    
    # Ensure destination is the last waypoint
    waypoints[-1] = RouteWaypoint(
        name=request.destination.title(),
        distance_from_start_km=round(distance_km, 1)
    )
    
    return RouteResult(
        origin=request.origin.title(),
        destination=request.destination.title(),
        total_distance_km=round(distance_km, 1),
        estimated_days=estimated_days,
        waypoints=waypoints
    )


def _get_mock_route(request: RouteRequest) -> RouteResult:
    """Fallback to mock data."""
    key = (request.origin.lower().strip(), request.destination.lower().strip())
    if key in MOCK_ROUTES:
        return MOCK_ROUTES[key]
    
    # Simple fall-back mock: 600km with evenly spaced waypoints
    total_distance = 600.0
    segments = [
        RouteWaypoint(name=f"Waypoint {i}", distance_from_start_km=i * 100.0)
        for i in range(1, 6)
    ]
    segments.append(RouteWaypoint(name=request.destination.title(), distance_from_start_km=total_distance))
    
    return RouteResult(
        origin=request.origin.title(),
        destination=request.destination.title(),
        total_distance_km=total_distance,
        estimated_days=max(1, int(total_distance / (request.preferred_daily_km or 100))),
        waypoints=segments,
    )
