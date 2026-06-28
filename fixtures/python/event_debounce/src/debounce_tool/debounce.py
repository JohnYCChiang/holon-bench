from __future__ import annotations


def debounce(events, window_ms):
    emitted = [e["id"] for e in events]
    return {"ok": True, "emitted": emitted}
