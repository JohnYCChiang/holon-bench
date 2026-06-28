from __future__ import annotations
from datetime import datetime, timedelta


def _expand(field, lo, hi):
    if field == "*":
        return set(range(lo, hi + 1))
    return {int(p) for p in field.split(",")}


def next_run(minute, hour, after):
    try:
        minutes = _expand(minute, 0, 59)
        hours = _expand(hour, 0, 23)
        base = datetime.strptime(after, "%Y-%m-%dT%H:%M:%S")
    except (ValueError, TypeError):
        return {"ok": False, "error": {"code": "invalid_field"}}
    candidate = base.replace(second=0)
    for _ in range(366 * 24 * 60):
        if candidate.hour in hours and candidate.minute in minutes:
            return {"ok": True, "next": candidate.strftime("%Y-%m-%dT%H:%M:%S")}
        candidate += timedelta(minutes=1)
    return {"ok": False, "error": {"code": "no_match"}}
