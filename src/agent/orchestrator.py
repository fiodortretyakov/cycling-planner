from __future__ import annotations

import os
import re
import uuid
import json
from typing import Dict, List, Optional, Tuple

import anthropic

from src.agent.schemas import ChatMessage, ChatRequest, ChatResponse, DayPlan
from src.tools.routes import RouteRequest, get_route
from src.tools.weather import WeatherRequest, get_weather
from src.tools.elevation import ElevationRequest, get_elevation_profile
from src.tools.accommodation import AccommodationRequest, find_accommodation
from src.tools.poi import get_points_of_interest, POIRequest


class ConversationMemory:
    def __init__(self) -> None:
        self.sessions: Dict[str, List[ChatMessage]] = {}

    def append(self, session_id: str, message: ChatMessage) -> None:
        self.sessions.setdefault(session_id, []).append(message)

    def get(self, session_id: str) -> List[ChatMessage]:
        return self.sessions.get(session_id, [])


def _extract_cities(text: str) -> Tuple[Optional[str], Optional[str]]:
    # Flexible matcher that stops at punctuation or the word "in" (common for dates/seasons)
    match = re.search(r"from\s+([A-Za-z\s]+?)\s+to\s+([A-Za-z\s]+?)(?:\s+in\s+|[\.,]|$)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None, None


def _extract_month(text: str) -> Optional[str]:
    months = [
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
    ]
    for month in months:
        if month in text.lower():
            return month.title()
    return None


def _extract_daily_distance(text: str) -> Optional[float]:
    match = re.search(r"(\d{2,3})\s?km", text.lower())
    if match:
        return float(match.group(1))
    return None


def _hostel_frequency(text: str) -> Optional[int]:
    match = re.search(r"hostel every (\d+)[a-z]* night", text.lower())
    if match:
        return int(match.group(1))
    return None


def _find_stop_for_distance(target: float, waypoints: List) -> str:
    closest = min(waypoints, key=lambda w: abs(w.distance_from_start_km - target))
    return closest.name


def _build_plan(
    route_result,
    daily_km: float,
    accommodation_pref: str,
    hostel_every: Optional[int],
    weather,
    elevation,
) -> List[DayPlan]:
    plans: List[DayPlan] = []
    total = route_result.total_distance_km
    distance_done = 0.0
    day = 1
    while distance_done < total:
        next_distance = min(distance_done + daily_km, total)
        stop_name = _find_stop_for_distance(next_distance, route_result.waypoints)
        stay_type = accommodation_pref
        if hostel_every and day % hostel_every == 0:
            stay_type = "hostel"
        options = find_accommodation(
            AccommodationRequest(location=stop_name, preference=stay_type)
        )
        accommodation = options[0]
        poi_list = get_points_of_interest(POIRequest(location=stop_name))
        note_parts = [f"POIs: {', '.join(p.name for p in poi_list)}"]
        plans.append(
            DayPlan(
                day=day,
                start=route_result.origin if day == 1 else plans[-1].end,
                end=stop_name,
                distance_km=round(next_distance - distance_done, 1),
                accommodation=f"{accommodation.name} ({accommodation.type})",
                weather=f"{weather.avg_temp_c}C avg, {weather.notes}",
                elevation=f"{elevation.total_elevation_gain_m}m gain over trip, {elevation.difficulty}",
                notes="; ".join(note_parts),
            )
        )
        distance_done = next_distance
        day += 1
    return plans


def _clarifying_questions(origin: Optional[str], destination: Optional[str], month: Optional[str]) -> List[str]:
    questions = []
    if not origin:
        questions.append("Where are you starting?")
    if not destination:
        questions.append("Where do you want to finish?")
    if not month:
        questions.append("Which month are you traveling?")
    return questions


def handle_chat(request: ChatRequest, memory: ConversationMemory) -> ChatResponse:
    session_id = request.session_id or str(uuid.uuid4())
    incoming = ChatMessage(role="user", content=request.message)
    memory.append(session_id, incoming)

    # Try to use Claude for intent extraction
    extracted = _extract_with_claude(request.message, memory.get(session_id))
    
    # Fallback to regex if Claude extraction fails
    if not extracted:
        extracted = _extract_with_regex(request.message, request.preferences)
    
    origin = extracted.get("origin")
    destination = extracted.get("destination")
    month = extracted.get("month")
    daily_km = extracted.get("daily_km")
    hostel_every = extracted.get("hostel_every")
    accommodation_pref = extracted.get("accommodation", "camping")

    questions = _clarifying_questions(origin, destination, month)
    if questions:
        # Use Claude to generate natural clarifying response
        response_text = _generate_clarifying_response_with_claude(questions, request.message)
        if not response_text:
            response_text = "I need a bit more detail before planning: " + " ".join(questions)
        
        assistant_msg = ChatMessage(role="assistant", content=response_text)
        memory.append(session_id, assistant_msg)
        return ChatResponse(
            session_id=session_id,
            messages=memory.get(session_id),
            clarifying_questions=questions,
            status="needs_clarification",
        )

    route = get_route(
        RouteRequest(
            origin=origin,
            destination=destination,
            preferred_daily_km=daily_km,
        )
    )
    weather = get_weather(WeatherRequest(location=destination, month=month or "June"))
    elevation = get_elevation_profile(ElevationRequest(origin=origin, destination=destination))

    preferred_daily = daily_km or 100.0
    plan = _build_plan(route, preferred_daily, accommodation_pref, hostel_every, weather, elevation)

    # Use Claude to generate natural response summary
    summary_text = _generate_plan_summary_with_claude(route, weather, elevation, plan, preferred_daily)
    if not summary_text:
        summary_text = (
            f"Planned {len(plan)} days from {route.origin} to {route.destination} "
            f"at ~{preferred_daily}km/day. "
            f"Weather around {weather.avg_temp_c}C with {weather.notes}. "
            f"Elevation: {elevation.difficulty}."
        )
    
    assistant_summary = ChatMessage(role="assistant", content=summary_text)
    memory.append(session_id, assistant_summary)

    return ChatResponse(session_id=session_id, messages=memory.get(session_id), day_plan=plan, status="ok")


def _extract_with_claude(message: str, conversation_history: List[ChatMessage]) -> Optional[Dict]:
    """Use Claude to extract trip parameters from natural language."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # Build conversation context
        history = "\n".join([f"{msg.role}: {msg.content}" for msg in conversation_history[:-1]])
        
        prompt = f"""Extract cycling trip parameters from this conversation.
Previous conversation:
{history}

Current message: {message}

Extract these parameters if mentioned:
- origin: starting city
- destination: ending city
- month: travel month
- daily_km: kilometers per day
- hostel_every: hostel every N nights
- accommodation: preference (camping/hostel/hotel)

Return ONLY a JSON object with the parameters found. Use null for missing values.
Example: {{"origin": "Amsterdam", "destination": "Copenhagen", "month": "June", "daily_km": 100, "hostel_every": 4, "accommodation": "camping"}}"""

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text.strip()
        # Extract JSON from response (might have markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        extracted = json.loads(response_text)
        # Filter out null values
        return {k: v for k, v in extracted.items() if v is not None}
    except Exception:
        return None


def _extract_with_regex(message: str, preferences: Optional[dict]) -> Dict:
    """Fallback regex extraction (original implementation)."""
    origin, destination = _extract_cities(message)
    month = _extract_month(message) or (preferences.get("month") if preferences else None)
    daily_km = _extract_daily_distance(message) or (preferences.get("daily_km") if preferences else None)
    hostel_every = _hostel_frequency(message) or (preferences.get("hostel_every") if preferences else None)
    accommodation_pref = preferences.get("accommodation", "camping") if preferences else "camping"
    
    return {
        "origin": origin,
        "destination": destination,
        "month": month,
        "daily_km": daily_km,
        "hostel_every": hostel_every,
        "accommodation": accommodation_pref,
    }


def _generate_clarifying_response_with_claude(questions: List[str], user_message: str) -> Optional[str]:
    """Use Claude to generate natural clarifying questions."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""The user said: "{user_message}"

I need to ask for these missing details:
{chr(10).join(f'- {q}' for q in questions)}

Generate a friendly, natural response asking for these details. Be conversational and helpful."""

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    except Exception:
        return None


def _generate_plan_summary_with_claude(route, weather, elevation, plan, daily_km) -> Optional[str]:
    """Use Claude to generate natural plan summary."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""Generate a brief, enthusiastic summary for this cycling trip plan:
- Route: {route.origin} to {route.destination}
- Distance: {route.total_distance_km}km over {len(plan)} days
- Daily average: {daily_km}km
- Weather: {weather.avg_temp_c}°C, {weather.notes}
- Terrain: {elevation.difficulty} ({elevation.total_elevation_gain_m}m elevation gain)

Make it conversational and encouraging, 2-3 sentences."""

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    except Exception:
        return None
