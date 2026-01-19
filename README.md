# cycling-planner

Conversational AI agent (FastAPI + Claude) that plans multi-day cycling trips using mocked tools for routing, accommodation, weather, and elevation. Built for the Affinity Labs technical assessment.

## How to run locally
- Create and activate a Python 3.10+ virtualenv.
- Install deps: `pip install -r requirements.txt`
- Start API: `uvicorn src.main:app --reload`
- Open `http://localhost:8000/docs` for the interactive Swagger UI.

## API
- `POST /chat` — Send `{ "session_id": "optional", "message": "text", "preferences": { ... } }` and receive a day-by-day plan plus clarifying questions if needed.
- `GET /health` — Liveness probe.

## Architecture decisions (brief)
- **Separation of concerns:** `src/agent` for orchestration and memory, `src/tools` for typed, reusable tool mocks, `src/api` for FastAPI routes.
- **Pydantic models:** All requests/responses are validated to keep the contract explicit.
- **Conversation state:** In-memory `ConversationMemory` keyed by `session_id` to maintain context between turns.
- **Tool-first planning:** The orchestrator extracts intent (route, month, daily km, accommodation cadence), calls tools, and assembles a daily itinerary with weather/elevation context.
- **Mocked integrations:** Tool outputs are deterministic mocks so behavior is testable without external APIs. Anthropic client is not invoked yet; the orchestration logic is deterministic for this exercise.

## What I would build with more time
- Replace mocks with real providers (routing APIs, booking data, weather/elevation services) and add caching.
- Add Anthropic Claude calls for richer NLU and natural responses while keeping tool-calling grounded.
- Persist conversation state (Redis/Postgres) and add authentication.
- Add budget and visa flows end-to-end, plus better POI selection per waypoint.

## Testing
- Run `pytest` to execute basic tool contract tests.
