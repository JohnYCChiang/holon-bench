from __future__ import annotations


def parse_retry_after(value, now_epoch):
    return {"ok": True, "delay_seconds": int(value), "kind": "seconds"}
