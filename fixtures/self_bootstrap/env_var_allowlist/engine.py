"""Frozen env-var allowlist filter. Do not edit — only the allowlist changes."""
from __future__ import annotations

import json
import pathlib


def load_allow(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "env_allow.json"
    return json.loads(target.read_text(encoding="utf-8"))


def is_allowed(allow: dict, profile: str, name: str) -> bool:
    """A var is exposed if it matches an exact name or a trailing-* prefix pattern."""
    for pattern in allow.get(profile, []):
        if pattern == name:
            return True
        if pattern.endswith("*") and name.startswith(pattern[:-1]):
            return True
    return False
