from __future__ import annotations

EXT = {".txt": "text/plain", ".json": "application/json", ".csv": "text/csv"}


def detect(data, filename=None):
    if filename:
        for ext, mime in EXT.items():
            if filename.endswith(ext):
                return {"ok": True, "mime": mime, "source": "extension"}
    return {"ok": True, "mime": "text/plain", "source": "default"}
