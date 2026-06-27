"""Frozen alias resolver. Do not edit — only the alias map changes."""
from __future__ import annotations

import json
import pathlib


def load_aliases(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "aliases.json"
    return json.loads(target.read_text(encoding="utf-8"))


def resolve(aliases: dict, name: str) -> str:
    """Follow the alias chain to a terminal name; raise ValueError on a cycle."""
    seen: set[str] = set()
    current = name
    while current in aliases:
        if current in seen:
            raise ValueError(f"alias cycle at {current}")
        seen.add(current)
        current = aliases[current]
    return current
