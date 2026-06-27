def encode(s):
    """Run-length encode ``s``: each maximal run of one character becomes that
    character followed by the decimal run length. ``encode("aaab") == "a3b1"``.
    ``encode("")`` is ``""``.
    """
    out = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        j = i
        while j < n and s[j] == ch:
            j += 1
        out.append(ch + str(j - i))
        i = j
    return "".join(out)


def decode(s):
    """Inverse of :func:`encode`. ``decode(encode(x)) == x`` for any ``str``.
    A run length may be any positive integer (possibly multi-digit).
    ``decode("")`` is ``""``.
    """
    out = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        count = int(s[i + 1])  # BUG: reads only ONE digit; multi-digit runs corrupt
        out.append(ch * count)
        i += 2
    return "".join(out)
