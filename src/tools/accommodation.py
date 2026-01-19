from __future__ import annotations

from typing import List
from pydantic import BaseModel


class AccommodationRequest(BaseModel):
    location: str
    preference: str


class AccommodationResult(BaseModel):
    location: str
    name: str
    type: str
    description: str


MOCK_ACCOMMODATION = {
    "hamburg": [
        AccommodationResult(
            location="Hamburg",
            name="Elbe Riverside Camp",
            type="camping",
            description="River-adjacent tent sites with showers",
        ),
        AccommodationResult(
            location="Hamburg",
            name="St. Pauli Hostel",
            type="hostel",
            description="Dorms near the city center",
        ),
    ],
    "copenhagen": [
        AccommodationResult(
            location="Copenhagen",
            name="City Cycle Hostel",
            type="hostel",
            description="Bike-friendly hostel with secure storage",
        ),
        AccommodationResult(
            location="Copenhagen",
            name="Amager Beach Camp",
            type="camping",
            description="Coastal camping with easy metro access",
        ),
    ],
}


def find_accommodation(request: AccommodationRequest) -> List[AccommodationResult]:
    key = request.location.lower().strip()
    options = MOCK_ACCOMMODATION.get(key)
    if options:
        return [opt for opt in options if opt.type == request.preference] or options
    # Fallback mock
    return [
        AccommodationResult(
            location=request.location.title(),
            name=f"{request.location.title()} {request.preference.title()} Option",
            type=request.preference,
            description="Mock accommodation recommendation",
        )
    ]
