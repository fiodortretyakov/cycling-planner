# cycling-planner

[![Tests](https://github.com/fiodortretyakov/cycling-planner/actions/workflows/test.yml/badge.svg)](https://github.com/fiodortretyakov/cycling-planner/actions/workflows/test.yml)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Conversational AI agent (FastAPI + Claude) that plans multi-day cycling trips using real public APIs with graceful fallbacks for routing, accommodation, weather, elevation, and POIs. Built for the Affinity Labs technical assessment.

## How to run locally

- Create and activate a Python 3.13+ virtualenv.
- Install deps: `pip install -r requirements.txt`
- Optional: create a `.env` file in the repo root (auto-loaded via python-dotenv in `src/main.py`):

  ```env
  ANTHROPIC_API_KEY=your_anthropic_key
  OPENROUTESERVICE_API_KEY=your_ors_key
  ```

- Start API: `uvicorn src.main:app --reload`
- Open `http://localhost:8000/docs` for the interactive Swagger UI.

## Try It

- Start the API locally:

  ```bash
  uvicorn src.main:app --reload
  ```

- Send a sample chat request:

  ```bash
  curl -sS -X POST http://localhost:8000/chat \
    -H 'Content-Type: application/json' \
    -d '{
      "session_id": "demo-1",
      "message": "Plan a June trip from Amsterdam to Copenhagen at ~100km/day with a hostel every 4 nights",
      "preferences": {"accommodation": "camping"}
    }' | jq .
  ```

  Tip: set `ANTHROPIC_API_KEY` in a `.env` file to enable Claude-enhanced extraction and summaries; otherwise the agent uses built-in fallbacks.

## API

- `POST /chat` — Send `{ "session_id": "optional", "message": "text", "preferences": { ... } }` and receive a day-by-day plan plus clarifying questions if needed.
- `GET /health` — Liveness probe.

## Architecture decisions (brief)

- **Separation of concerns:** `src/agent` for orchestration and memory, `src/tools` for typed, reusable tool implementations, `src/api` for FastAPI routes.
- **Pydantic models:** All requests/responses are validated to keep the contract explicit.
- **Conversation state:** In-memory `ConversationMemory` keyed by `session_id` to maintain context between turns.
- **NLU with Claude + fallback:** When `ANTHROPIC_API_KEY` is available, the agent uses Anthropic Claude to extract intent, ask clarifying questions, and generate summaries. If not, it falls back to deterministic regex/logic so the system still works offline.
- **Tool-first planning:** The orchestrator extracts intent (route, month, daily km, accommodation cadence), calls tools, and assembles a daily itinerary with weather/elevation context.
- **Real API integrations with fallbacks:**
  - **Routing:** OpenRouteService (requires key) or Nominatim geocoding + Haversine fallback.
  - **Accommodation:** OpenStreetMap Overpass API.
  - **Weather:** Open-Meteo archive (no key required).
  - **Elevation:** Open-Elevation API.
  - **POIs:** OpenStreetMap Overpass API.
  - All tools degrade to mock/heuristic data when APIs are unavailable.

## CI/CD

- GitHub Actions runs tests and coverage on push/PR (see `.github/workflows/test.yml`).
- A smoke job runs `scripts/smoke_anthropic.py` with the repo's `ANTHROPIC_API_KEY` secret to verify Anthropic connectivity/auth. Low-credit errors are treated as success to confirm wiring without failing the build.

## Testing

- Unit tests are designed to run fast by mocking network calls (httpx helpers), so no external API traffic occurs during test runs.
- Run `pytest` to execute tests locally. Coverage reports (XML/HTML) are generated via `pytest-cov`.

## What I would build with more time

- Persist conversation state (Redis/Postgres) and add authentication.
- Add richer budget and visa flows end-to-end, with improved POI selection per waypoint.
- Implement caching and retry/backoff for external APIs.
- Create an interactive frontend for better user experience.
