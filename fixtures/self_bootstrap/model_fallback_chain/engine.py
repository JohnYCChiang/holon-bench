"""Frozen model fallback resolver. Do not edit — only the fallback map changes."""
from __future__ import annotations

import json
import pathlib


def load_fallback(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "fallback.json"
    return json.loads(target.read_text(encoding="utf-8"))


def resolve_chain(cfg: dict, start: str | None = None) -> list:
    """Ordered fallback chain from start, following 'fallback' edges to a terminal.

    Raises ValueError on a cycle.
    """
    node = start if start is not None else cfg.get("start")
    edges = cfg.get("fallback", {})
    chain: list = []
    seen: set = set()
    while node is not None:
        if node in seen:
            raise ValueError(f"fallback cycle at {node}")
        seen.add(node)
        chain.append(node)
        node = edges.get(node)
    return chain
