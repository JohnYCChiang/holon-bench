from __future__ import annotations


class CancellationToken:
    def __init__(self) -> None:
        self.cancelled = False

    def cancel(self) -> None:
        self.cancelled = True


def process_batch(items: list[int], worker, token: CancellationToken) -> dict:
    results = []
    for item in items:
        results.append(worker(item))
    return {"ok": True, "cancelled": False, "results": results, "processed": len(results)}
