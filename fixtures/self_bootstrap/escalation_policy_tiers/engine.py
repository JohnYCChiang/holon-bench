"""Frozen escalation engine. Do not edit — only the escalation policy changes."""
from __future__ import annotations

import json
import pathlib


def load_policy(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "escalation.json"
    return json.loads(target.read_text(encoding="utf-8"))


def escalate(policy: dict, failures: int) -> str:
    """Return the action for the highest threshold whose min_failures <= failures."""
    action = policy.get("default_action", "ignore")
    best = -1
    for rule in policy.get("thresholds", []):
        minimum = int(rule.get("min_failures", 0))
        if failures >= minimum and minimum > best:
            best = minimum
            action = rule.get("action", action)
    return action
