from __future__ import annotations

from pathlib import Path


def write_text_atomic(path: str | Path, text: str, fail_after_temp: bool = False) -> dict:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    if fail_after_temp:
        raise RuntimeError("simulated failure")
    return {"ok": True, "path": str(target), "bytes": len(text.encode("utf-8"))}
