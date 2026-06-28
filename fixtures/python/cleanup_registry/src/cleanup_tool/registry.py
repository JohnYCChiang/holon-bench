from __future__ import annotations


class CleanupRegistry:
    def __init__(self):
        self._handlers = []

    def register(self, name, fn):
        self._handlers.append((name, fn))

    def run_all(self):
        ran = []
        for name, fn in self._handlers:
            fn()
            ran.append(name)
        return {"ok": True, "ran": ran, "errors": [], "completed": True}
