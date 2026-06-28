from __future__ import annotations


class TokenBucket:
    def __init__(self, capacity, refill_per_sec, now=0.0):
        self.capacity = float(capacity)
        self.refill_per_sec = float(refill_per_sec)
        self.tokens = float(capacity)
        self.updated = float(now)

    def allow(self, now, cost=1):
        if self.tokens >= cost:
            self.tokens -= cost
            return {"ok": True, "allowed": True, "remaining": self.tokens}
        return {"ok": True, "allowed": False, "remaining": self.tokens}
