"""Frozen worker-pool allocator. Do not edit — only the pool plan changes."""
from __future__ import annotations

import json
import pathlib


def load_pools(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "pools.json"
    return json.loads(target.read_text(encoding="utf-8"))


def pool_for(cfg: dict, cls: str) -> str:
    return cfg.get("class_to_pool", {}).get(cls, "default")


def capacity(cfg: dict, pool: str) -> int:
    return int(cfg.get("pools", {}).get(pool, 0))


def is_valid(cfg: dict) -> bool:
    """Pools fit the global budget, honour per-pool minimums, and every mapped
    class targets a real pool."""
    pools = cfg.get("pools", {})
    total = int(cfg.get("total_workers", 0))
    mins = cfg.get("min_workers", {})
    if sum(int(v) for v in pools.values()) > total:
        return False
    for name, cap in pools.items():
        if int(cap) < int(mins.get(name, 0)):
            return False
    for cls, pool in cfg.get("class_to_pool", {}).items():
        if pool not in pools:
            return False
    return True
