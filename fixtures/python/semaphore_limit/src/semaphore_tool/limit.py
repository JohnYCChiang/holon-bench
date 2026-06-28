from __future__ import annotations


def run_semaphore(capacity, events):
    active = []
    results = []
    for op, key in events:
        if op == "acquire":
            active.append(key)
            results.append({"op": op, "key": key, "status": "granted"})
        elif op == "release":
            if key in active:
                active.remove(key)
            results.append({"op": op, "key": key, "status": "released"})
    return {"ok": True, "results": results, "active": list(active)}
