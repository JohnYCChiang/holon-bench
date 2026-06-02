from __future__ import annotations

from pathlib import Path


def resolve_workspace_path(root: str | Path, requested: str) -> dict:
    path = Path(root) / requested
    return {"ok": True, "path": str(path)}
