# MysteryBox — The Blackout Protocol

A playable, deterministic detective-thriller MVP. Start a seeded case, search three locations, interrogate four distinct witnesses, collect evidence, reconstruct a visible timeline, and submit an evidence-weighted verdict. The solution is generated on the server and is never returned by normal investigation endpoints.

## What is implemented

- FastAPI game engine with seeded generation and validation.
- Eight scenario-dependent evidence items across laboratory, security, and quarters.
- Three unreliable-testimony paths: deliberate deflection, faulty memory, and selective omission.
- Player-safe REST API, location-gated discovery, evidence-gated confrontation, and final report.
- Cinematic responsive React/Vite client with text interrogation (English, Hindi, and Hinglish input is accepted as text).
- 100-seed deterministic test suite; the current authored combinatorics produce at least 20 distinct culprit/motive/method variants across those seeds.

## Deliberate limitations

Gnani Prisma and Timbre endpoints are not guessed. `POST /api/voice/transcribe` and `POST /api/voice/speak` exist as backend-only fail-closed integration boundaries: without credentials and a verified official contract they return a transparent 503, while text play remains usable. This is intentionally not represented as a real voice integration. The current store is in-memory for the MVP, so restarting the backend clears investigations; SQLite persistence is the next production increment.

## Run locally

Requires Python 3.10+ and Node 20+. On Windows, use a real Python installation rather than the Microsoft Store `python`/`py` aliases. Python 3.12–3.14 is the most conservative choice; this repository also runs on the existing Python 3.15 environment after the `uvicorn[standard]` extra was removed.

```powershell
cd backend
# Replace this path with your actual Python executable if needed.
& "C:\msys64\ucrt64\bin\python.exe" -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL (normally `http://localhost:5173`). The OpenAPI page is at `http://localhost:8000/docs`.

Or, after installing both dependency sets once, launch them together from the repository root:

```powershell
.\start-dev.ps1
```

The Vite development server proxies `/api` to FastAPI, so a local game uses one browser origin and no longer depends on browser CORS behavior. If the backend is stopped, the game now reports that explicitly instead of the unhelpful browser message “Failed to fetch”.

## Test

```powershell
cd backend
python -m pytest -q
```

## Environment

Copy the repository-root `.env.example` to the repository-root `.env`; do not expose any API key to the frontend. `GNANI_API_BASE_URL` and product keys are reserved for the verified official API contract.

### Optional grounded dialogue with Groq

Set `MYSTERYBOX_LLM_PROVIDER=groq` and add a server-side `GROQ_API_KEY` to enable the Groq adapter. It uses the OpenAI-compatible chat-completions endpoint and defaults to `llama-3.3-70b-versatile`. The LLM only rephrases a response already selected by the deterministic engine; it cannot choose the culprit, create evidence, or change the timeline. With no key or a failed provider call, the tested deterministic dialogue remains in use.

## Demo path

1. Open a new investigation. The server locks a random seed and canonical solution.
2. Inspect all three locations and collect their leads.
3. Ask Vikram about the time, Elena about the meeting, and the remaining suspects about access.
4. Review evidence and the timeline, then submit a verdict.
5. The report reveals the solution only after submission; open another case to generate a new truth.

## Deployment

Deploy `backend` as a Python ASGI service and `frontend` as a static Vite build (`npm run build`). Set `VITE_API_URL` to the public backend origin at build time and restrict FastAPI CORS to that deployed frontend origin.
