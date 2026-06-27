"""Frozen backup-retention resolver. Do not edit — only the tier table changes."""
from __future__ import annotations

import json
import pathlib


def load_retention(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "retention.json"
    return json.loads(target.read_text(encoding="utf-8"))


def keep_interval(cfg: dict, age_days: int):
    """Keep-every interval for the first tier covering age_days, else None (drop).

    Tiers are evaluated in listed order.
    """
    for tier in cfg.get("tiers", []):
        if age_days <= int(tier["up_to_days"]):
            return int(tier["every_days"])
    return None
