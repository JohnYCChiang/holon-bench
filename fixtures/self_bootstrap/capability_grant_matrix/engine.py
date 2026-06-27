"""Frozen capability authorizer. Do not edit — only the grant matrix changes."""
from __future__ import annotations

import json
import pathlib


def load_matrix(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "capabilities.json"
    return json.loads(target.read_text(encoding="utf-8"))


def authorize(matrix: dict, role: str, action: str) -> str:
    """Return 'allow' iff role is granted action in the matrix, else 'deny'."""
    grants = matrix.get("grants", {})
    if action in grants.get(role, []):
        return "allow"
    return "deny"
