"""Frozen priority lane resolver. Do not edit — only the lane assignments change."""
from __future__ import annotations

import json
import pathlib


def load_lanes(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "lanes.json"
    return json.loads(target.read_text(encoding="utf-8"))


def lane_of(cfg: dict, job: str) -> str:
    return cfg.get("assignments", {}).get(job, cfg.get("default", "standard"))


def priority(cfg: dict, job: str) -> int:
    """Lower index = higher priority, per lane_order."""
    order = cfg.get("lane_order", [])
    lane = lane_of(cfg, job)
    return order.index(lane) if lane in order else len(order)
