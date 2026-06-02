from __future__ import annotations

from pathlib import Path


def scan_files(root: str, exclude_globs: list[str] | None = None, max_bytes: int = 1024) -> dict:
    base = Path(root)
    exclude_globs = exclude_globs or []
    files: list[str] = []
    skipped = {"binary": 0, "hidden": 0, "ignored": 0, "too_large": 0}
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(base).as_posix()
        if any(path.match(pattern) or rel == pattern for pattern in exclude_globs):
            skipped["ignored"] += 1
            continue
        files.append(rel)
    return {"files": sorted(files), "skipped": skipped}
