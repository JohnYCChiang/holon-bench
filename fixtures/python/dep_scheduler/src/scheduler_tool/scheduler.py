from __future__ import annotations


def resolve_order(tasks):
    return {"ok": True, "order": sorted(tasks.keys())}
