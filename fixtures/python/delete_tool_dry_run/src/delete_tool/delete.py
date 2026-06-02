from __future__ import annotations

from pathlib import Path


def delete_paths(root: str, paths: list[str], dry_run: bool = False) -> dict:
    base = Path(root).resolve()
    deleted: list[str] = []
    for item in paths:
        target = (base / item).resolve()
        if not str(target).startswith(str(base)):
            return {"ok": False, "error": {"code": "unsafe_path", "message": item}}
        if target.exists():
            target.unlink()
            deleted.append(item)
    cache = base / ".holon" / "cache" / "delete.log"
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text("\n".join(deleted))
    return {"ok": True, "deleted": deleted}
