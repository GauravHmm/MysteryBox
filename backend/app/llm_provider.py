"""Optional Groq dialogue polisher; the deterministic engine remains canonical."""
from __future__ import annotations
import json
import os
from urllib.error import URLError
from urllib.request import Request, urlopen

def polish_dialogue(*, character_name: str, speech_style: str, player_message: str, canonical_response: str) -> str:
    """Rephrase a fixed response only; never grants a model story-authoring authority."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or os.getenv("MYSTERYBOX_LLM_PROVIDER", "deterministic") != "groq":
        return canonical_response
    payload = {"model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"), "temperature": 0.55, "max_tokens": 120,
               "messages": [
                   {"role": "system", "content": "You are polishing a line in a locked detective game. Preserve every factual claim exactly. Never add names, evidence, times, admissions, explanations, or facts. Return one natural spoken sentence only."},
                   {"role": "user", "content": f"Character: {character_name}. Style: {speech_style}. Player asked: {player_message!r}. Canonical response: {canonical_response!r}"},
               ]}
    request = Request("https://api.groq.com/openai/v1/chat/completions", data=json.dumps(payload).encode(), headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=12) as response:
            text = json.loads(response.read())["choices"][0]["message"]["content"].strip()
        return text if 3 <= len(text) <= 700 else canonical_response
    except (URLError, KeyError, IndexError, TimeoutError, ValueError, json.JSONDecodeError):
        return canonical_response
