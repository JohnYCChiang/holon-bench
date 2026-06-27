"""Frozen secret-rotation auditor. Do not edit — only the rotation schedule changes."""
from __future__ import annotations

import datetime
import json
import pathlib


def load_json(name: str) -> dict:
    return json.loads((pathlib.Path(__file__).resolve().parent / name).read_text(encoding="utf-8"))


def _days(rotated_on: str, today: str) -> int:
    return (datetime.date.fromisoformat(today) - datetime.date.fromisoformat(rotated_on)).days


def is_expired(cfg: dict, secret: str, today: str) -> bool:
    """A secret is expired (and alerts) when days since rotation exceed its interval."""
    rule = cfg.get(secret)
    if not rule:
        return False
    return _days(rule["rotated_on"], today) > int(rule["interval_days"])
