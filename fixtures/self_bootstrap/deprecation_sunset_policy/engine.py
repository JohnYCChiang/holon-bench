"""Frozen deprecation lifecycle resolver. Do not edit — only the policy changes."""
from __future__ import annotations

import json
import pathlib


def load_sunset(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "sunset.json"
    return json.loads(target.read_text(encoding="utf-8"))


def status(cfg: dict, version: str, today: str) -> str:
    """active -> deprecated -> removed, by ISO date thresholds (no entry = active)."""
    rule = cfg.get(version)
    if not rule:
        return "active"
    if today >= rule.get("sunset_on", "9999-12-31"):
        return "removed"
    if today >= rule.get("deprecated_on", "9999-12-31"):
        return "deprecated"
    return "active"
