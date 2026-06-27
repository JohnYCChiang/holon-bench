"""Frozen feature-flag evaluator. Do not edit — only the flag config changes."""
from __future__ import annotations

import hashlib
import json
import pathlib


def load_flags(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "flags.json"
    return json.loads(target.read_text(encoding="utf-8"))


def _bucket(user_id: str) -> int:
    digest = hashlib.sha256(user_id.encode("utf-8")).hexdigest()
    return int(digest, 16) % 100


def is_enabled(flags: dict, flag: str, user_id: str) -> bool:
    """Return True if the flag is on for this user (allowlist or rollout bucket)."""
    rule = flags.get(flag)
    if not rule or not rule.get("enabled", False):
        return False
    if user_id in rule.get("allowlist", []):
        return True
    return _bucket(user_id) < int(rule.get("rollout_percent", 0))
