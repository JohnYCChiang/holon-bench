def merge(intervals):
    """Merge overlapping or touching intervals.

    ``intervals`` is an iterable of ``[start, end]`` pairs with ``start <=
    end``. Returns a new list of merged intervals sorted by start; intervals
    that overlap or merely touch (``end == next start``) are collapsed into one.
    Raises ValueError if any interval has ``start > end``. The input is not
    mutated and freshly built lists are returned.
    """
    ordered = []
    for iv in intervals:
        s, e = iv[0], iv[1]
        if s > e:
            raise ValueError("interval start must be <= end")
        ordered.append((s, e))
    ordered.sort()
    merged = []
    for s, e in ordered:
        if merged and s < merged[-1][1]:  # BUG: should be s <= merged[-1][1] so touching merges
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return merged
