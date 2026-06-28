from __future__ import annotations


def compute_backoff(attempt, base_ms=100, factor=2, cap_ms=2000):
    delay = base_ms * (factor ** attempt)
    return {"ok": True, "attempt": attempt, "delay_ms": delay}
