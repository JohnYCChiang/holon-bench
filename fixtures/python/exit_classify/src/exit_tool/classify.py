from __future__ import annotations


def classify_exit(returncode):
    if returncode == 0:
        return {"ok": True, "status": "success", "exit_code": 0, "signal": None}
    return {"ok": False, "status": "error", "exit_code": returncode, "signal": None}
