from __future__ import annotations


def run_tool(payload: dict) -> dict:
    if "path" not in payload:
        return {"ok": False, "error": "missing path"}
    if payload.get("path") == "":
        return {"ok": False, "error": "empty path"}
    return {"ok": True, "path": payload["path"], "indexed": 1}
