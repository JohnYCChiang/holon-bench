"""Frozen severity classifier. Do not edit — only the severity map changes."""
from __future__ import annotations

import json
import pathlib


def load_severity_map(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "severity.json"
    return json.loads(target.read_text(encoding="utf-8"))


def classify(tags: list[str], severity_map: dict) -> str:
    """Return 'block' if any tag maps to 'critical', else 'allow'."""
    for tag in tags:
        if severity_map.get(tag) == "critical":
            return "block"
    return "allow"
