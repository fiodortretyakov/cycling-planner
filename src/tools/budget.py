from __future__ import annotations

from pydantic import BaseModel


class BudgetRequest(BaseModel):
    days: int
    accommodation_mix: dict


class BudgetResult(BaseModel):
    estimated_total_eur: float
    breakdown: dict


def estimate_budget(request: BudgetRequest) -> BudgetResult:
    camping_cost = 20
    hostel_cost = 45
    hotel_cost = 90
    nights = request.days - 1 if request.days > 1 else 1
    camping_nights = nights * request.accommodation_mix.get("camping", 0)
    hostel_nights = nights * request.accommodation_mix.get("hostel", 0)
    hotel_nights = nights * request.accommodation_mix.get("hotel", 0)
    estimated_total = camping_nights * camping_cost + hostel_nights * hostel_cost + hotel_nights * hotel_cost
    breakdown = {
        "camping": camping_nights * camping_cost,
        "hostel": hostel_nights * hostel_cost,
        "hotel": hotel_nights * hotel_cost,
    }
    return BudgetResult(estimated_total_eur=estimated_total, breakdown=breakdown)
