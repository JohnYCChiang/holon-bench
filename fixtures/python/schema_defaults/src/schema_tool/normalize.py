from __future__ import annotations


def normalize_request(payload: dict) -> dict:
    return {"ok": True, "request": payload}
