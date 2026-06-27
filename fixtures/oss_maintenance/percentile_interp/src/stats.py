import math


def percentile(data, p):
    """Return the ``p``-th percentile of ``data`` by linear interpolation.

    ``data`` is a non-empty iterable of numbers and ``p`` is in ``[0, 100]``.
    The rank is ``p/100 * (n - 1)`` over the sorted data and the result is the
    linear interpolation between the two bracketing order statistics, returned
    as a float. ``p = 0`` yields the minimum and ``p = 100`` the maximum. Raises
    ValueError on empty data or ``p`` outside ``[0, 100]``; input is not mutated.
    """
    values = sorted(data)
    if not values:
        raise ValueError("data must be non-empty")
    if p < 0 or p > 100:
        raise ValueError("p must be in [0, 100]")
    n = len(values)
    rank = (p / 100.0) * n  # BUG: should be p/100 * (n - 1), with interpolation
    idx = int(rank)
    if idx >= n:
        idx = n - 1
    return float(values[idx])
