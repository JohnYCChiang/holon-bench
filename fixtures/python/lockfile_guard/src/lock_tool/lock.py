from __future__ import annotations

import os


def run_locked(lock_path, fn):
    if os.path.exists(lock_path):
        return {"ok": False, "error": {"code": "locked", "message": "lock already held"}}
    with open(lock_path, "w") as handle:
        handle.write(str(os.getpid()))
    value = fn()
    os.unlink(lock_path)
    return {"ok": True, "value": value}
