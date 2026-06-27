VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def roman_to_int(s):
    """Convert an uppercase Roman numeral string to its integer value.

    Subtractive pairs (``IV``, ``IX``, ``XL``, ``XC``, ``CD``, ``CM``) encode a
    smaller symbol placed before a larger one. An empty string is ``0``. A
    character outside ``IVXLCDM`` raises ``ValueError``.
    """
    total = 0
    for ch in s:
        if ch not in VALUES:
            raise ValueError(f"invalid roman numeral character: {ch}")
        # BUG: always adds each symbol's value and never subtracts, so
        # subtractive pairs like "IV" are read as 1+5=6 instead of 4.
        total += VALUES[ch]
    return total
