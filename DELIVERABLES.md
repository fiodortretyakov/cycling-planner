# Deliverables Checklist

## ✅ 1. Public GitHub Repository

- **Status:** COMPLETE
- **URL:** <https://github.com/fiodortretyakov/cycling-planner>
- **Visibility:** Public ✓
- **License:** MIT ✓

## ✅ 2. README with Complete Documentation

### ✅ How to Run Locally

Located at the top of [README.md](README.md):

- Python 3.13+ virtualenv setup
- Pip install requirements
- Optional .env configuration for API keys
- Starting the API with uvicorn
- Opening Swagger UI at <http://localhost:8000/docs>

### ✅ Architecture Decisions (< 1 page)

Included in README.md - "Architecture decisions (brief)" section covers:

- Separation of concerns (agent, tools, API layers)
- Pydantic validation
- Conversation state management
- NLU with Claude + regex fallback
- Tool-first planning approach
- Real API integrations with graceful degradation

### ✅ What I Would Develop with More Time

Included in README.md - "What I would build with more time" section:

- Persist conversation state (Redis/Postgres) + authentication
- Richer budget and visa flows end-to-end
- Caching and retry/backoff for external APIs
- Interactive frontend for better UX

## ⏳ 3. Screen Recording - NEEDS TO BE CREATED

### How to Create the Demo Recording

You need to create a screen recording showing a full conversation flow. Here's how:

#### Option A: Using Built-in Tools (Recommended)

```bash
# 1. Start the API
.venv/bin/python -m uvicorn src.main:app --reload

# 2. In another terminal, test the API
curl -sS -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "demo-1",
    "message": "Plan a June trip from Amsterdam to Copenhagen at ~100km/day with a hostel every 4 nights",
    "preferences": {"accommodation": "camping"}
  }' | jq .

# The response will show the complete trip plan with:
# - Day-by-day itinerary
# - Accommodation options
# - Weather information
# - Elevation profiles
# - Points of interest
```

#### Option B: Using Swagger UI (Better for Demo)

1. Start the API: `.venv/bin/python -m uvicorn src.main:app --reload`
2. Open <http://localhost:8000/docs>
3. Expand the `/chat` endpoint
4. Click "Try it out"
5. Input your demo message
6. Click "Execute"
7. Scroll to see the full response

#### Recording Tools

- **macOS:** QuickTime Player (built-in)
- **Windows:** Xbox Game Bar (Win + G) or OBS
- **Linux:** OBS Studio or SimpleScreenRecorder

#### Demo Conversation Flow (Suggested)

```
User: "Plan a cycling trip from Berlin to Prague in July at 80km/day"
↓
API: Asks clarifying questions if needed
↓
User: Provides more details if needed
↓
API: Returns complete trip plan with:
   - Day 1: Berlin → [waypoint] (xx km)
   - Day 2: [waypoint] → [waypoint] (xx km)
   - ... continuing to Prague
   
   Plus for each day/location:
   - Accommodation options (hotels, hostels, camping)
   - Weather forecast
   - Elevation gains
   - Nearby attractions/POIs
```

### File Locations for Recording

After creating the recording, save it as:

- `docs/demo-recording.mp4` or
- `docs/demo-recording.webm` or
- Link to video on YouTube/Google Drive in the README

### Update README with Video Link

Add to the top of README.md after badges:

```markdown
## Demo
[Watch a full conversation demo](docs/demo-recording.mp4) showing trip planning from start to finish.
```

---

## Summary

- ✅ Public repository: READY
- ✅ README complete: READY
- ⏳ Demo recording: AWAITING CREATION

**Next Step:** Create the screen recording following the options above and save it to the repository!
