from __future__ import annotations
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .domain import generate, discover, public_evidence, reply, timeline, verdict, LOCATIONS, MOTIVES
from .integrations import unavailable

app = FastAPI(title="MysteryBox API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], allow_methods=["*"], allow_headers=["*"])
STORE = {}

class NewCase(BaseModel): seed: int | None = Field(default=None, ge=0, le=2_147_483_647)
class Move(BaseModel): location: str
class Interrogate(BaseModel): character_id: str; message: str = Field(min_length=1, max_length=1000); evidence_id: str | None = None
class Verdict(BaseModel): culprit: str; motive: str; evidence_ids: list[str] = []; explanation: str = Field(default="", max_length=3000)
def case_or_404(investigation_id: str):
    if investigation_id not in STORE: raise HTTPException(404, "Investigation not found")
    return STORE[investigation_id]
def guard(fn):
    try: return fn()
    except (KeyError, ValueError) as err: raise HTTPException(400, str(err))

@app.get("/health")
def health(): return {"status": "ok", "voice_mode": "mock-until-verified-gnani-contract"}
@app.post("/api/voice/transcribe")
def transcribe(): return unavailable("prisma")
@app.post("/api/voice/speak")
def speak(): return unavailable("timbre")
@app.get("/api/meta")
def meta(): return {"motives": [{"id": k, "label": v} for k,v in MOTIVES.items()]}
@app.post("/api/cases/new")
def new_case(body: NewCase):
    case = generate(body.seed); STORE[case.id] = case; return case.public()
@app.get("/api/investigations/{investigation_id}")
def get_case(investigation_id: str): return case_or_404(investigation_id).public()
@app.post("/api/investigations/{investigation_id}/move")
def move(investigation_id: str, body: Move):
    case = case_or_404(investigation_id)
    if body.location not in LOCATIONS: raise HTTPException(400, "Unknown location")
    case.location = body.location; return case.public()
@app.post("/api/investigations/{investigation_id}/evidence/discover/{evidence_id}")
def find_evidence(investigation_id: str, evidence_id: str): return guard(lambda: discover(case_or_404(investigation_id), evidence_id))
@app.get("/api/investigations/{investigation_id}/evidence")
def evidence(investigation_id: str): return public_evidence(case_or_404(investigation_id))
@app.get("/api/investigations/{investigation_id}/timeline")
def get_timeline(investigation_id: str): return timeline(case_or_404(investigation_id))
@app.post("/api/investigations/{investigation_id}/interrogate")
def interrogate(investigation_id: str, body: Interrogate): return guard(lambda: reply(case_or_404(investigation_id), body.character_id, body.message, body.evidence_id))
@app.post("/api/investigations/{investigation_id}/verdict")
def submit_verdict(investigation_id: str, body: Verdict): return guard(lambda: verdict(case_or_404(investigation_id), body.model_dump()))
