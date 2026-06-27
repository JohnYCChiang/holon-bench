def jaccard(a, b):
    """Return the Jaccard similarity of two iterables, treated as sets.

    The similarity is ``|a & b| / |a | b|`` as a float in ``[0, 1]``. Duplicate
    elements within an input are ignored. Two empty inputs are identical, so
    ``jaccard([], [])`` is ``1.0``.
    """
    sa = set(a)
    sb = set(b)
    intersection = len(sa & sb)
    # BUG: the union size is taken as len(a) + len(b), which double-counts the
    # shared elements (and miscounts duplicates) instead of |a | b|.
    union = len(a) + len(b)
    return intersection / union
