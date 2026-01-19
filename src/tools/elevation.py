from __future__ import annotations

from pydantic import BaseModel


class ElevationRequest(BaseModel):
    origin: str
    destination: str


class ElevationResult(BaseModel):
    total_elevation_gain_m: float
    difficulty: str


def get_elevation_profile(request: ElevationRequest) -> ElevationResult:
    # Simple heuristic mock: coastal routes are easy; mountainous are hard
    if any(city.lower() in {"bergen", "innsbruck", "geneva"} for city in [request.origin, request.destination]):
        return ElevationResult(total_elevation_gain_m=5200.0, difficulty="hard")
    return ElevationResult(total_elevation_gain_m=1800.0, difficulty="moderate")
