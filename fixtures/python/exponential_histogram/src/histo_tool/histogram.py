import math


def histogram(values, base):
    if base <= 1:
        return {"ok": False, "error": {"code": "invalid_base"}}
    counts = {}
    for v in values:
        if v <= 0:
            return {"ok": False, "error": {"code": "invalid_value"}}
        e = math.floor(math.log(v, base))
        counts[e] = counts.get(e, 0) + 1
    buckets = [[exp, counts[exp]] for exp in counts]
    return {"ok": True, "buckets": buckets, "total": len(values)}
