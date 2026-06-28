from __future__ import annotations


class IdempotentRunner:
    def __init__(self):
        self._cache = {}

    def run(self, key, fn):
        value = fn()
        return {"ok": True, "value": value, "cached": False}
