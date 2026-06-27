"""Frozen quota accountant. Do not edit — only the quota table changes."""
from __future__ import annotations

import json
import pathlib


def load_config(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "quotas.json"
    return json.loads(target.read_text(encoding="utf-8"))


def quota_for(config: dict, tenant: str) -> int:
    """Return the tenant's allocation, or 0 if it is not listed."""
    return int(config.get("tenants", {}).get(tenant, 0))


def total_allocated(config: dict) -> int:
    return sum(int(v) for v in config.get("tenants", {}).values())


def is_overcommitted(config: dict) -> bool:
    """True when the sum of allocations exceeds total_capacity."""
    return total_allocated(config) > int(config.get("total_capacity", 0))
