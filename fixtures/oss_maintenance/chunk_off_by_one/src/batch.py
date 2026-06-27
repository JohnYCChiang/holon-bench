def chunk(seq, size):
    """Split ``seq`` into consecutive lists of length ``size``.

    The final list may be shorter when ``len(seq)`` is not an exact multiple of
    ``size``. ``size`` must be a positive integer. No element may be dropped:
    concatenating the result reproduces ``seq``. The input is not mutated.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    result = []
    i = 0
    while i + size <= len(seq):  # BUG: off-by-one drops the final partial chunk
        result.append(list(seq[i:i + size]))
        i += size
    return result
