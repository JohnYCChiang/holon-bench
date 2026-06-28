from __future__ import annotations


def truncate_bytes(text, max_bytes):
    kept = text[:max_bytes]
    return {
        "ok": True,
        "text": kept,
        "truncated": len(text) > max_bytes,
        "byte_count": len(kept),
        "omitted_bytes": len(text) - len(kept),
    }
