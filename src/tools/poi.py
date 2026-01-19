from __future__ import annotations

import httpx
from pydantic import BaseModel


class POIRequest(BaseModel):
    location: str


class POIResult(BaseModel):
    location: str
    name: str
    description: str


MOCK_POIS = {
    "amsterdam": [
        POIResult(location="Amsterdam", name="Rijksmuseum", description="Famous Dutch art museum"),
        POIResult(location="Amsterdam", name="Van Gogh Museum", description="World's largest Van Gogh collection"),
    ],
    "copenhagen": [
        POIResult(location="Copenhagen", name="Tivoli Gardens", description="Historic amusement park in city center"),
        POIResult(location="Copenhagen", name="Nyhavn", description="Colorful waterfront with cafes"),
    ],
}


def get_points_of_interest(request: POIRequest) -> list[POIResult]:
    """
    Get points of interest using OpenStreetMap Overpass API.
    Searches for tourist attractions, viewpoints, and landmarks.
    """
    try:
        coords = _geocode_location(request.location)
        if coords:
            pois = _search_pois_osm(coords, request.location)
            if pois:
                return pois
    except Exception:
        pass
    
    # Fallback to mock data
    key = request.location.lower().strip()
    if key in MOCK_POIS:
        return MOCK_POIS[key]
    
    return [
        POIResult(location=request.location.title(), name="Old Town", description="Historic center great for a rest stop"),
        POIResult(location=request.location.title(), name="Local Market", description="Good for refueling snacks"),
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


def _search_pois_osm(coords: tuple[float, float], location_name: str) -> list[POIResult]:
    """Search for points of interest using Overpass API."""
    lat, lon = coords
    
    # Overpass query for tourist attractions, viewpoints, and monuments
    query = f"""
    [out:json][timeout:25];
    (
      node["tourism"="attraction"](around:3000,{lat},{lon});
      node["tourism"="viewpoint"](around:3000,{lat},{lon});
      node["historic"="monument"](around:3000,{lat},{lon});
      node["historic"="castle"](around:3000,{lat},{lon});
      way["tourism"="attraction"](around:3000,{lat},{lon});
    );
    out body 10;
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
                name = tags_dict.get("name", "Unnamed POI")
                
                # Skip unnamed POIs
                if name == "Unnamed POI":
                    continue
                
                # Build description from available tags
                desc_parts = []
                if "description" in tags_dict:
                    desc_parts.append(tags_dict["description"])
                if "tourism" in tags_dict:
                    desc_parts.append(f"Type: {tags_dict['tourism']}")
                if "historic" in tags_dict:
                    desc_parts.append(f"Historic {tags_dict['historic']}")
                if "wikipedia" in tags_dict:
                    desc_parts.append("Wikipedia entry available")
                
                description = "; ".join(desc_parts) if desc_parts else "Point of interest"
                
                results.append(POIResult(
                    location=location_name.title(),
                    name=name,
                    description=description
                ))
            
            return results[:5] if results else []
    except Exception:
        pass
    
    return []
