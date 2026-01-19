#!/usr/bin/env python
"""
Integration test for real API calls (optional, not run in CI by default).

To run with real APIs:
    export ANTHROPIC_API_KEY=your_key
    export OPENROUTESERVICE_API_KEY=your_key
    python scripts/integration_test.py

This will test actual API integrations without mocks.
"""

import os
import sys
from src.tools.routes import get_route, RouteRequest
from src.tools.weather import get_weather, WeatherRequest
from src.tools.accommodation import find_accommodation, AccommodationRequest
from src.tools.elevation import get_elevation_profile, ElevationRequest
from src.tools.poi import get_points_of_interest, POIRequest


def test_apis():
    """Test real API calls if keys are available."""
    
    print("=" * 60)
    print("INTEGRATION TEST: Real API Calls")
    print("=" * 60)
    
    has_anthropic_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    has_ors_key = bool(os.environ.get("OPENROUTESERVICE_API_KEY"))
    
    print(f"\n✓ Anthropic key available: {has_anthropic_key}")
    print(f"✓ OpenRouteService key available: {has_ors_key}")
    
    # Test 1: Routes
    print("\n" + "=" * 60)
    print("Test 1: Getting cycling route...")
    try:
        route = get_route(RouteRequest(
            origin="Berlin",
            destination="Prague",
            preferred_daily_km=80
        ))
        print(f"✓ Route: {route.origin} → {route.destination}")
        print(f"  Distance: {route.total_distance_km}km over {route.estimated_days} days")
        print(f"  Waypoints: {len(route.waypoints)}")
    except Exception as e:
        print(f"✗ Route failed: {e}")
    
    # Test 2: Weather
    print("\n" + "=" * 60)
    print("Test 2: Getting weather...")
    try:
        weather = get_weather(WeatherRequest(
            location="Prague",
            month="July"
        ))
        print(f"✓ Weather in {weather.location} ({weather.month})")
        print(f"  Temp: {weather.avg_temp_c}°C")
        print(f"  Precip: {weather.precipitation_mm}mm")
        print(f"  Notes: {weather.notes}")
    except Exception as e:
        print(f"✗ Weather failed: {e}")
    
    # Test 3: Accommodation
    print("\n" + "=" * 60)
    print("Test 3: Finding accommodation...")
    try:
        accom = find_accommodation(AccommodationRequest(
            location="Prague",
            preference="hostel"
        ))
        print(f"✓ Found {len(accom)} accommodation option(s)")
        for option in accom[:2]:
            print(f"  - {option.name} ({option.type}): {option.description}")
    except Exception as e:
        print(f"✗ Accommodation failed: {e}")
    
    # Test 4: Elevation
    print("\n" + "=" * 60)
    print("Test 4: Getting elevation profile...")
    try:
        elevation = get_elevation_profile(ElevationRequest(
            origin="Berlin",
            destination="Prague"
        ))
        print(f"✓ Elevation profile")
        print(f"  Gain: {elevation.total_elevation_gain_m}m")
        print(f"  Difficulty: {elevation.difficulty}")
    except Exception as e:
        print(f"✗ Elevation failed: {e}")
    
    # Test 5: POIs
    print("\n" + "=" * 60)
    print("Test 5: Getting points of interest...")
    try:
        pois = get_points_of_interest(POIRequest(location="Prague"))
        print(f"✓ Found {len(pois)} POI(s)")
        for poi in pois[:2]:
            print(f"  - {poi.name}: {poi.description}")
    except Exception as e:
        print(f"✗ POI failed: {e}")
    
    print("\n" + "=" * 60)
    print("Integration test complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_apis()
