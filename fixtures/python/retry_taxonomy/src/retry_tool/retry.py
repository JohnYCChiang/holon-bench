from __future__ import annotations


class ToolFailure(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def run_with_retry(fn, max_attempts: int = 3) -> dict:
    try:
        return {"ok": True, "value": fn()}
    except ToolFailure as exc:
        return {"ok": False, "error": {"code": exc.code}}
