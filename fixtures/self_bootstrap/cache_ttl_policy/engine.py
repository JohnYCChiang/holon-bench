"""Frozen cache-TTL resolver. Do not edit — only the TTL table changes."""
from __future__ import annotations

import json
import pathlib


def load_config(path: str | None = None) -> dict:
    target = pathlib.Path(path) if path else pathlib.Path(__file__).resolve().parent / "ttl.json"
    return json.loads(target.read_text(encoding="utf-8"))


def get_ttl(config: dict, resource: str) -> int:
    """Return the TTL for a resource, or default_ttl when it is not listed."""
    return int(config.get("ttls", {}).get(resource, config.get("default_ttl", 0)))
