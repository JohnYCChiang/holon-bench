"""Frozen sandbox scope checker. Do not edit — only the scope grants change."""
from __future__ import annotations

import json
import pathlib


def load_scopes(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "scopes.json"
    return json.loads(target.read_text(encoding="utf-8"))


def permits(grant: str, action: str) -> bool:
    """A grant permits itself, anything nested under it, or all under '*'."""
    if grant == "*" or grant == action:
        return True
    return action.startswith(grant + ":")


def allowed(scopes: dict, profile: str, action: str) -> bool:
    return any(permits(grant, action) for grant in scopes.get(profile, []))
