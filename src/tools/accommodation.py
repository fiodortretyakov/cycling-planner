from __future__ import annotations

import httpx
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
    """
    Find accommodation using OpenStreetMap Overpass API.
    Searches for camping, hostels, hotels near the location.
    """
    # Try to get real accommodation data
    try:
        coords = _geocode_location(request.location)
        if coords:
            results = _search_accommodation_osm(coords, request.preference)
            if results:
                return results
    except Exception:
        pass
    
    # Fallback to mock data
    key = request.location.lower().strip()
    options = MOCK_ACCOMMODATION.get(key)
    if options:
        return [opt for opt in options if opt.type == request.preference] or options
    
    # Final fallback
    return [
        AccommodationResult(
            location=request.location.title(),
            name=f"{request.location.title()} {request.preference.title()} Option",
            type=request.preference,
            description="Mock accommodation recommendation",
        )
    ]


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


def _search_accommodation_osm(coords: tuple[float, float], preference: str) -> List[AccommodationResult]:
    """Search for accommodation using Overpass API."""
    lat, lon = coords
    
    # Map preference to OSM tags
    tag_map = {
        "camping": "tourism=camp_site",
        "hostel": "tourism=hostel",
        "hotel": "tourism=hotel",
    }
    
    tags = tag_map.get(preference, "tourism=hotel")
    
    # Overpass query
    query = f"""
    [out:json][timeout:25];
    (
      node[{tags}](around:5000,{lat},{lon});
      way[{tags}](around:5000,{lat},{lon});
    );
    out body 5;
    """
    
    try:
        url = "https://overpass-api.de/api/interpreter"
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, data={"data": query})
            response.raise_for_status()
            data = response.json()
            
            results = []
            for element in data.get("elements", []):
                tags_dict = element.get("tags", {})
                name = tags_dict.get("name", "Unnamed")
                
                # Build description from available tags
                desc_parts = []
                if "description" in tags_dict:
                    desc_parts.append(tags_dict["description"])
                if "stars" in tags_dict:
                    desc_parts.append(f"{tags_dict['stars']} stars")
                if "website" in tags_dict:
                    desc_parts.append(f"Website available")
                
                description = "; ".join(desc_parts) if desc_parts else f"{preference.title()} near {coords}"
                
                results.append(AccommodationResult(
                    location=f"Near {lat:.2f}, {lon:.2f}",
                    name=name,
                    type=preference,
                    description=description
                ))
            
            return results[:3]  # Return top 3 results
    except Exception:
        pass
    
    return []
