def truncate_utf8(text, max_bytes):
    """Return the longest prefix of ``text`` whose UTF-8 encoding fits within
    ``max_bytes`` bytes without splitting a multi-byte character.

    A character whose encoding does not fully fit is dropped, never split. The
    function must not raise on any valid ``str`` input. ``max_bytes`` must be a
    non-negative integer.
    """
    if max_bytes < 0:
        raise ValueError("max_bytes must be non-negative")
    return text.encode("utf-8")[:max_bytes].decode("utf-8")  # BUG: splits chars
