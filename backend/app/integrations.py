"""Fail-closed Gnani integration boundary.

The public build intentionally does not guess Gnani endpoints or payloads.  Once
the official Prisma/Timbre contract is supplied, this is the only module that
needs wiring; browser clients never receive either API key.
"""
import os
from fastapi import HTTPException

def unavailable(product: str):
    key = os.getenv(f"GNANI_{product.upper()}_API_KEY")
    base = os.getenv("GNANI_API_BASE_URL")
    if not key or not base:
        raise HTTPException(503, {"code": "GNANI_NOT_CONFIGURED", "message": f"Gnani {product.title()} is unavailable. Text mode remains active; configure a verified official contract server-side."})
    raise HTTPException(501, {"code": "GNANI_CONTRACT_REQUIRED", "message": "Credentials are configured but no request schema has been verified. Refusing to invent an API contract."})
