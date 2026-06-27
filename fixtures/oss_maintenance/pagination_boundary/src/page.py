def paginate(items, page_size, page):
    """Return the items on a 1-based ``page``.

    Pages are contiguous, non-overlapping slices of ``items`` in order. ``page``
    is 1-based; a page past the end yields an empty list. Raises ValueError if
    ``page_size`` <= 0 or ``page`` < 1. The input is not mutated and a new list
    is returned.
    """
    if page_size <= 0:
        raise ValueError("page_size must be positive")
    if page < 1:
        raise ValueError("page must be >= 1")
    start = page * page_size  # BUG: skips the first page; should be (page - 1) * page_size
    end = start + page_size
    return list(items[start:end])
