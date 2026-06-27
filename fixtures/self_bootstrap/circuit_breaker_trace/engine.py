"""Frozen circuit-breaker simulator. Do not edit — only the breaker config changes."""
from __future__ import annotations

import json
import pathlib


def load_json(name: str) -> dict:
    return json.loads((pathlib.Path(__file__).resolve().parent / name).read_text(encoding="utf-8"))


def replay(config: dict, outcomes: list[str]) -> dict:
    """Replay outcomes; the breaker trips at failure_threshold consecutive fails."""
    threshold = int(config.get("failure_threshold", 1))
    consecutive = 0
    max_consecutive = 0
    tripped = False
    for outcome in outcomes:
        if outcome == "fail":
            consecutive += 1
            max_consecutive = max(max_consecutive, consecutive)
            if consecutive >= threshold:
                tripped = True
        else:
            consecutive = 0
    return {"tripped": tripped, "max_consecutive": max_consecutive}
