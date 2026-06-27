"""Frozen idempotency replay engine. Do not edit — only the window config changes."""
from __future__ import annotations

import json
import pathlib


def load_json(name: str) -> dict:
    return json.loads((pathlib.Path(__file__).resolve().parent / name).read_text(encoding="utf-8"))


def process(cfg: dict, events: list) -> list:
    """Replay events; a key seen within window_seconds of its last accept is a dup."""
    window = int(cfg.get("window_seconds", 0))
    last_accept: dict = {}
    out: list = []
    for ev in events:
        key = ev["key"]
        ts = int(ev["ts"])
        prev = last_accept.get(key)
        if prev is not None and ts - prev <= window:
            out.append("duplicate")
        else:
            out.append("accepted")
            last_accept[key] = ts
    return out
