from __future__ import annotations


def chunk(items, size):
    batches = []
    for start in range(0, len(items) - size + 1, size):
        batches.append(items[start:start + size])
    return {"ok": True, "batches": batches, "count": len(batches)}
