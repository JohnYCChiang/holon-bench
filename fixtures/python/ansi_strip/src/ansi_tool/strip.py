from __future__ import annotations


def strip_ansi(text):
    clean = text
    return {"ok": True, "clean": clean, "stripped": 0, "length": len(clean)}
