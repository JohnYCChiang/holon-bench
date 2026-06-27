"""Frozen quality gate. Do not edit — only the threshold config changes."""
from __future__ import annotations

import json
import pathlib


def load_thresholds(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "thresholds.json"
    return json.loads(target.read_text(encoding="utf-8"))


def gate(thresholds: dict, metrics: dict) -> str:
    """Return 'reject' if any metric is below its minimum, else 'accept'."""
    for key, minimum in thresholds.items():
        if metrics.get(key, 0) < minimum:
            return "reject"
    return "accept"
