_UNITS = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]


def humanize(n):
    """Render a non-negative byte count using binary (1024) units, one decimal
    place, e.g. ``humanize(1536) == "1.5 KiB"``. ``humanize(0) == "0 B"``.
    Negative input raises ValueError.
    """
    if n < 0:
        raise ValueError("byte count must be non-negative")
    if n == 0:
        return "0 B"
    size = float(n)
    idx = 0
    while size >= 1024 and idx < len(_UNITS) - 1:
        size /= 1024
        idx += 1
    # BUG: a value that rounds UP to 1024.0 at one decimal place is shown as
    # "1024.0 <unit>" instead of rolling over to the next unit as "1.0 <next>".
    return "{:.1f} {}".format(size, _UNITS[idx])
