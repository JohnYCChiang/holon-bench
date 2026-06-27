"""Frozen schema migration planner. Do not edit — only the migration map changes."""
from __future__ import annotations

import json
import pathlib
from collections import deque


def load_migrations(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "migrations.json"
    return json.loads(target.read_text(encoding="utf-8"))


def find_path(migrations: dict, start: str, end: str) -> list[str] | None:
    """Shortest version path start..end over directed migration steps, or None.

    Ties are broken by the lexicographically smaller next version (deterministic).
    """
    graph: dict[str, list[str]] = {}
    for step in migrations.get("steps", []):
        graph.setdefault(step["from"], []).append(step["to"])
    queue: deque[list[str]] = deque([[start]])
    seen = {start}
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == end:
            return path
        for nxt in sorted(graph.get(node, [])):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(path + [nxt])
    return None
