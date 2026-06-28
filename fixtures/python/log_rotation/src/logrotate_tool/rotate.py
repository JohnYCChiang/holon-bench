from __future__ import annotations

import os


def rotate(path, max_bytes, backups=3):
    if os.path.getsize(path) < max_bytes:
        return {"ok": True, "rotated": False, "removed": [], "backups_present": []}
    os.replace(path, path + ".1")
    open(path, "w").close()
    return {"ok": True, "rotated": True, "removed": [], "backups_present": [path + ".1"]}
