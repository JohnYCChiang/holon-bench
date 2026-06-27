"""Frozen task dispatcher. Do not edit — only the routing table changes."""
from __future__ import annotations

import json
import pathlib


def load_routing(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "routing.json"
    return json.loads(target.read_text(encoding="utf-8"))


def dispatch(routing: dict, task_type: str) -> str:
    """Return the worker that handles task_type, or the table default."""
    routes = routing.get("routes", {})
    if task_type in routes:
        return routes[task_type]
    return routing.get("default", "unrouted")
