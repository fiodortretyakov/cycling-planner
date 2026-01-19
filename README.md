# cycling-planner

Conversational AI agent (FastAPI + Claude) that plans multi-day cycling trips using mocked tools for routing, accommodation, weather, and elevation. Built for the Affinity Labs technical assessment.

## How to run locally
- Create and activate a Python 3.10+ virtualenv.
- Install deps: `pip install -r requirements.txt`
- (Optional) Set environment variables for enhanced API features:
  - `OPENROUTESERVICE_API_KEY` - For real routing data via OpenRouteService
  - `ANTHROPIC_API_KEY` - For AI-powered responses (future feature)
- Start API: `uvicorn src.main:app --reload`
- Open `http://localhost:8000/docs` for the interactive Swagger UI.

## API
- `POST /chat` — Send `{ "session_id": "optional", "message": "text", "preferences": { ... } }` and receive a day-by-day plan plus clarifying questions if needed.
- `GET /health` — Liveness probe.

## Architecture decisions (brief)
- **Separation of concerns:** `src/agent` for orchestration and memory, `src/tools` for typed, reusable tool implementations, `src/api` for FastAPI routes.
- **Pydantic models:** All requests/responses are validated to keep the contract explicit.
- **Conversation state:** In-memory `ConversationMemory` keyed by `session_id` to maintain context between turns.
- **Tool-first planning:** The orchestrator extracts intent (route, month, daily km, accommodation cadence), calls tools, and assembles a daily itinerary with weather/elevation context.
- **Real API integrations with fallbacks:** Tools now integrate with real public APIs:
  - **Routing:** OpenRouteService API (requires key) or Nominatim geocoding + Haversine distance calculation
  - **Accommodation:** OpenStreetMap Overpass API for real places
  - **Weather:** Open-Meteo historical archive API (free, no key required)
  - **Elevation:** Open-Elevation API for terrain profiles
  - All tools gracefully fall back to mock data if APIs are unavailable or return no results

## What I would build with more time
- Add Anthropic Claude calls for richer NLU and natural responses while keeping tool-calling grounded.
- Persist conversation state (Redis/Postgres) and add authentication.
- Add budget and visa flows end-to-end, plus better POI selection per waypoint.
- Implement caching for API responses to reduce latency and API costs.
- Add retry logic and better error handling for external APIs.
- Create an interactive frontend for better user experience.

## Testing
- Run `pytest` to execute basic tool contract tests.
