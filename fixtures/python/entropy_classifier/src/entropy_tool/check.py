from __future__ import annotations


def classify(value, min_length=16, min_entropy=3.5):
    distinct = len(set(value))
    entropy = distinct / len(value) if value else 0.0
    return {
        "ok": True,
        "entropy": round(entropy, 4),
        "likely_secret": entropy >= min_entropy,
        "length": len(value),
    }
