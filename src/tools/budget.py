from __future__ import annotations

from pydantic import BaseModel


class BudgetRequest(BaseModel):
    days: int
    accommodation_mix: dict
    country: str = "netherlands"  # Default country for pricing


class BudgetResult(BaseModel):
    estimated_total_eur: float
    breakdown: dict


# Average daily costs in EUR for different countries and accommodation types
# Based on typical cyclist budget travel costs (2024-2026 estimates)
COUNTRY_COSTS = {
    "netherlands": {
        "camping": 25,
        "hostel": 50,
        "hotel": 95,
        "food_per_day": 35,
        "misc_per_day": 15,
    },
    "denmark": {
        "camping": 30,
        "hostel": 60,
        "hotel": 120,
        "food_per_day": 45,
        "misc_per_day": 20,
    },
    "germany": {
        "camping": 20,
        "hostel": 45,
        "hotel": 85,
        "food_per_day": 30,
        "misc_per_day": 15,
    },
    "france": {
        "camping": 22,
        "hostel": 48,
        "hotel": 90,
        "food_per_day": 35,
        "misc_per_day": 18,
    },
    "belgium": {
        "camping": 23,
        "hostel": 48,
        "hotel": 90,
        "food_per_day": 32,
        "misc_per_day": 15,
    },
    "sweden": {
        "camping": 28,
        "hostel": 55,
        "hotel": 110,
        "food_per_day": 42,
        "misc_per_day": 20,
    },
    "norway": {
        "camping": 35,
        "hostel": 65,
        "hotel": 130,
        "food_per_day": 50,
        "misc_per_day": 25,
    },
    "spain": {
        "camping": 18,
        "hostel": 35,
        "hotel": 70,
        "food_per_day": 28,
        "misc_per_day": 12,
    },
    "italy": {
        "camping": 20,
        "hostel": 40,
        "hotel": 80,
        "food_per_day": 32,
        "misc_per_day": 15,
    },
}

# Default costs for unknown countries (moderate Western European pricing)
DEFAULT_COSTS = {
    "camping": 22,
    "hostel": 48,
    "hotel": 90,
    "food_per_day": 35,
    "misc_per_day": 15,
}


def estimate_budget(request: BudgetRequest) -> BudgetResult:
    """
    Estimate cycling trip budget with realistic country-specific costs.
    Includes accommodation, food, and miscellaneous expenses.
    """
    country_key = request.country.lower().strip()
    costs = COUNTRY_COSTS.get(country_key, DEFAULT_COSTS)
    
    nights = request.days - 1 if request.days > 1 else 1
    
    # Calculate accommodation costs
    camping_nights = nights * request.accommodation_mix.get("camping", 0)
    hostel_nights = nights * request.accommodation_mix.get("hostel", 0)
    hotel_nights = nights * request.accommodation_mix.get("hotel", 0)
    
    camping_cost = camping_nights * costs["camping"]
    hostel_cost = hostel_nights * costs["hostel"]
    hotel_cost = hotel_nights * costs["hotel"]
    
    total_accommodation = camping_cost + hostel_cost + hotel_cost
    
    # Calculate food and misc costs for all days
    food_cost = request.days * costs["food_per_day"]
    misc_cost = request.days * costs["misc_per_day"]
    
    # Additional one-time costs
    bike_maintenance = request.days * 2  # ~2 EUR per day for minor repairs/maintenance
    
    estimated_total = total_accommodation + food_cost + misc_cost + bike_maintenance
    
    breakdown = {
        "accommodation": {
            "camping": round(camping_cost, 2),
            "hostel": round(hostel_cost, 2),
            "hotel": round(hotel_cost, 2),
            "total": round(total_accommodation, 2),
        },
        "food": round(food_cost, 2),
        "miscellaneous": round(misc_cost, 2),
        "bike_maintenance": round(bike_maintenance, 2),
        "daily_average": round(estimated_total / request.days, 2),
    }
    
    return BudgetResult(
        estimated_total_eur=round(estimated_total, 2),
        breakdown=breakdown
    )
