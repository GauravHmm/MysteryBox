"""Deterministic, player-safe game domain for The Blackout Protocol."""
from __future__ import annotations

import random
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

CHARACTERS = {
    "mira": {"name": "Dr. Mira Kapoor", "role": "Senior research scientist", "style": "precise, composed"},
    "aarav": {"name": "Aarav Malhotra", "role": "Research associate", "style": "defensive, emotionally charged"},
    "vikram": {"name": "Vikram Sethi", "role": "Security supervisor", "style": "quiet, procedural"},
    "elena": {"name": "Elena D'Souza", "role": "Research coordinator", "style": "articulate, carefully evasive"},
}
LOCATIONS = {
    "laboratory": {"name": "Main Research Laboratory", "description": "A restricted chamber stands open beneath emergency lights."},
    "security": {"name": "Security Control Room", "description": "Monitors stutter through gaps in a storm-damaged recording."},
    "quarters": {"name": "Residential Quarters", "description": "Private doors and damp coats keep their own counsel."},
}
MOTIVES = {
    "protect_research": "Protect a dangerous research result from disclosure",
    "expose_coverup": "Expose an unethical cover-up before it disappeared",
    "personal_debt": "Stop Adrian from revealing a personal financial betrayal",
    "career_pressure": "Prevent Adrian from ending a career-defining project",
}
METHODS = {
    "security_override": "used a security override during the blackout",
    "maintenance_diversion": "created a maintenance diversion and moved through the service corridor",
    "access_clone": "used cloned access credentials to enter the restricted chamber",
    "recording_gap": "exploited the camera reboot window after the power surge",
}

@dataclass
class Investigation:
    id: str
    seed: int
    culprit: str
    motive: str
    method: str
    false_memory: str
    omission: str
    evidence: dict[str, dict[str, Any]]
    discovered: set[str] = field(default_factory=set)
    history: dict[str, list[dict[str, str]]] = field(default_factory=dict)
    location: str = "laboratory"
    state: str = "INVESTIGATING"
    started_at: float = field(default_factory=time.time)
    completed_at: float | None = None

    def public(self) -> dict[str, Any]:
        return {
            "id": self.id, "seed": self.seed, "state": self.state, "location": self.location,
            "case": {"title": "The Blackout Protocol", "tagline": "Four witnesses. One disappearance. A different truth every time.",
                     "incident": "At 11:47 PM, backup generators restored power. Dr. Adrian Sen was gone; his phone lay outside the laboratory."},
            "characters": [{"id": key, **value} for key, value in CHARACTERS.items()],
            "locations": [{"id": key, **value} for key, value in LOCATIONS.items()],
            "evidence_count": len(self.discovered), "evidence_total": len(self.evidence),
            "objectives": ["Inspect the facility", "Test witness accounts", "Reconstruct 11:20–11:47 PM", "Submit an evidence-backed verdict"],
        }

def generate(seed: int | None = None) -> Investigation:
    seed = seed if seed is not None else random.SystemRandom().randint(10000, 99999999)
    rng = random.Random(seed)
    people = list(CHARACTERS)
    culprit = rng.choice(people)
    others = [p for p in people if p != culprit]
    motive = rng.choice(list(MOTIVES))
    method = rng.choice(list(METHODS))
    false_memory, omission = rng.sample(others, 2)
    evidence = _evidence(culprit, motive, method, false_memory, omission)
    case = Investigation(str(uuid.uuid4()), seed, culprit, motive, method, false_memory, omission, evidence)
    validate(case)
    return case

def _evidence(culprit: str, motive: str, method: str, false_memory: str, omission: str) -> dict[str, dict[str, Any]]:
    return {
        "phone": {"name": "Damaged phone", "location": "laboratory", "description": "Adrian's phone stopped recording at 11:41 PM after a struggle near the restricted door.", "establishes": "A confrontation occurred before the generators returned.", "relates": [culprit]},
        "access_log": {"name": "Restricted entry log", "location": "security", "description": f"A credential assigned to {CHARACTERS[culprit]['name']} opened the restricted chamber at 11:34 PM.", "establishes": "The culprit's credentials reached the chamber.", "relates": [culprit]},
        "camera_gap": {"name": "Camera reboot report", "location": "security", "description": "Storm surge caused a 43-second recording gap at 11:39 PM.", "establishes": "The footage cannot settle the disappearance alone.", "relates": [culprit]},
        "research_note": {"name": "Encrypted research note", "location": "laboratory", "description": f"Adrian wrote: 'If they learn about the {MOTIVES[motive].lower()}, I have to release the protocol.'", "establishes": "Adrian intended to act on a serious conflict.", "relates": [culprit]},
        "maintenance": {"name": "Maintenance report", "location": "security", "description": f"The override path was consistent with someone who {METHODS[method]}.", "establishes": "The blackout provided a specific opportunity.", "relates": [culprit]},
        "message": {"name": "Unsent personal message", "location": "quarters", "description": f"A message draft shows {CHARACTERS[omission]['name']} knew Adrian planned a private meeting at 11:30 PM but omitted it.", "establishes": "One account is selectively incomplete.", "relates": [omission]},
        "statement": {"name": "Witness statement correction", "location": "quarters", "description": f"{CHARACTERS[false_memory]['name']} placed the generator alarm at 11:32 PM; the system log puts it at 11:38 PM.", "establishes": "One contradiction is a faulty memory, not necessarily a lie.", "relates": [false_memory]},
        "voice_note": {"name": "Fragmented voice note", "location": "quarters", "description": "Adrian says, 'Meet me by the restricted door. Bring the override.'", "establishes": "The meeting was planned and access was central.", "relates": [culprit]},
    }

def validate(case: Investigation) -> None:
    assert case.culprit in CHARACTERS and case.false_memory != case.culprit
    assert len(case.evidence) >= 7
    assert {e["location"] for e in case.evidence.values()} == set(LOCATIONS)
    assert sum(case.culprit in e["relates"] for e in case.evidence.values()) >= 4

def discover(case: Investigation, evidence_id: str) -> dict[str, Any]:
    if evidence_id not in case.evidence: raise KeyError("Unknown evidence")
    item = case.evidence[evidence_id]
    if item["location"] != case.location: raise ValueError("That evidence is not at the current location")
    case.discovered.add(evidence_id)
    return {"id": evidence_id, **item}

def public_evidence(case: Investigation) -> list[dict[str, Any]]:
    return [{"id": ident, **case.evidence[ident]} for ident in case.evidence if ident in case.discovered]

def timeline(case: Investigation) -> list[dict[str, str]]:
    items = [{"time": "11:20 PM", "label": "Storm intensifies", "status": "confirmed"}, {"time": "11:30 PM", "label": "Private meeting planned", "status": "unverified"}, {"time": "11:34 PM", "label": "Restricted door accessed", "status": "confirmed" if "access_log" in case.discovered else "unknown"}, {"time": "11:39 PM", "label": "Camera reboot window", "status": "confirmed" if "camera_gap" in case.discovered else "unknown"}, {"time": "11:41 PM", "label": "Phone recording ends", "status": "confirmed" if "phone" in case.discovered else "unknown"}, {"time": "11:47 PM", "label": "Generators return; Adrian missing", "status": "confirmed"}]
    return items

def reply(case: Investigation, character: str, message: str, evidence_id: str | None = None) -> dict[str, Any]:
    if character not in CHARACTERS: raise KeyError("Unknown character")
    lower = message.lower()
    if evidence_id and evidence_id not in case.discovered: raise ValueError("Evidence must be discovered before it can be presented")
    if evidence_id and character == case.culprit and character in case.evidence[evidence_id]["relates"]:
        text = "That record does not tell you why I was there. The blackout distorted everything—but I won't deny it puts me at the door."
        intent = "partial_admission"
    elif character == case.false_memory and any(word in lower for word in ("time", "alarm", "11:32", "11:38")):
        text = "I remember the alarm earlier. If the log says otherwise, then the storm—or my nerves—has scrambled the sequence."
        intent = "memory_correction"
    elif character == case.omission and any(word in lower for word in ("meeting", "message", "adrian")):
        text = "There was a meeting planned. I left it out because it was private, not because I caused Adrian's disappearance."
        intent = "selective_omission"
    elif character == case.culprit and any(word in lower for word in ("laboratory", "door", "access", "where")):
        text = "I was dealing with the blackout. I did not expect Adrian to be at the restricted chamber."
        intent = "deflection"
    else:
        text = {"mira": "Be exact with your question. Assumptions are how investigations fail.", "aarav": "I already told security what I saw. The storm made everyone jumpy.", "vikram": "The logs are more reliable than memory tonight. Start there.", "elena": "I can help with facts, Detective. I won't decorate them for you."}[character]
        intent = "guarded_response"
    case.history.setdefault(character, []).append({"player": message, "character": text})
    return {"dialogue": text, "intent": intent, "mentioned_topics": ["blackout"], "possible_followup_topics": ["access log", "timeline"], "mock_voice": True}

def verdict(case: Investigation, payload: dict[str, Any]) -> dict[str, Any]:
    if case.state == "COMPLETED": raise ValueError("Verdict already submitted")
    selected = payload.get("culprit")
    motive = payload.get("motive")
    supporting = set(payload.get("evidence_ids", [])) & case.discovered
    culprit_points = 45 if selected == case.culprit else 0
    motive_points = 25 if motive == case.motive else 0
    evidence_points = min(20, len(supporting & {"access_log", "research_note", "maintenance", "phone", "voice_note"}) * 5)
    timeline_points = 10 if len(supporting) >= 3 else 0
    score = culprit_points + motive_points + evidence_points + timeline_points
    case.state, case.completed_at = "COMPLETED", time.time()
    return {"score": score, "accusation": payload, "solution": {"culprit": case.culprit, "culprit_name": CHARACTERS[case.culprit]["name"], "motive": case.motive, "motive_label": MOTIVES[case.motive], "method": METHODS[case.method], "false_memory": case.false_memory, "selective_omission": case.omission}, "missed_evidence": [k for k in case.evidence if k not in case.discovered], "explanation": f"{CHARACTERS[case.culprit]['name']} {METHODS[case.method]} to {MOTIVES[case.motive].lower()}. The access record, opportunity trail, and Adrian's material form the deducible route."}
