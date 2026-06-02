from __future__ import annotations


def run_tool(payload: dict) -> dict:
    if "path" not in payload:
        return {"ok": False, "error": {"code": "missing_path", "message": "missing path"}}
    if payload.get("path") == "":
        return {"ok": False, "error": {"code": "empty_path", "message": "empty path"}}
    return {"ok": True, "path": payload["path"], "indexed": 1}
