"""Frozen webhook fan-out resolver. Do not edit — only subscriptions change."""
from __future__ import annotations

import json
import pathlib


def load_subscriptions(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "subscriptions.json"
    return json.loads(target.read_text(encoding="utf-8"))


def subscribers(subs: dict, event: str) -> list:
    """Deterministic sorted set of subscribers for an event, including wildcard '*'."""
    result = set(subs.get(event, []))
    result |= set(subs.get("*", []))
    return sorted(result)


def delivers(subs: dict, event: str, subscriber: str) -> bool:
    return subscriber in subscribers(subs, event)
