from __future__ import annotations

from typing import List
from pydantic import BaseModel


class POIRequest(BaseModel):
    location: str


class POIResult(BaseModel):
    location: str
    name: str
    description: str


def get_points_of_interest(request: POIRequest) -> List[POIResult]:
    return [
        POIResult(location=request.location.title(), name="Old Town", description="Historic center great for a rest stop"),
        POIResult(location=request.location.title(), name="Local Market", description="Good for refueling snacks"),
    ]
