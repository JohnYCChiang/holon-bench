from __future__ import annotations

import json
from pathlib import Path


def cache_key(name: str) -> str:
    return name.replace("/", "_")


def write_cache(cache_dir: str | Path, name: str, data: dict) -> dict:
    path = Path(cache_dir) / f"{cache_key(name)}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return {"ok": True, "path": str(path), "written": True}
