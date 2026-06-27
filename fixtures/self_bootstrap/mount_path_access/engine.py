"""Frozen mount access resolver. Do not edit — only the mount rules change."""
from __future__ import annotations

import json
import pathlib


def load_mounts(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "mounts.json"
    return json.loads(target.read_text(encoding="utf-8"))


def access(mounts: dict, profile: str, path: str) -> str:
    """Mode of the longest matching path-prefix rule, else 'none'."""
    best_mode = "none"
    best_len = -1
    for rule in mounts.get(profile, []):
        base = rule["path"]
        norm = base.rstrip("/")
        if path == base or path == norm or path.startswith(norm + "/"):
            if len(norm) > best_len:
                best_len = len(norm)
                best_mode = rule["mode"]
    return best_mode
