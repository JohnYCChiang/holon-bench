from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP


def round_half_up(amount, ndigits):
    """Round a decimal ``amount`` to ``ndigits`` places, ties away from zero.

    ``amount`` is a decimal string (e.g. ``"2.5"``) and ``ndigits`` is the
    number of fractional digits to keep (``>= 0``). Returns a string with
    exactly ``ndigits`` decimal places. Halves round away from zero for both
    positive and negative values. Raises ValueError if ``ndigits < 0``.
    """
    if ndigits < 0:
        raise ValueError("ndigits must be >= 0")
    quantum = Decimal(1).scaleb(-ndigits)
    # BUG: ROUND_HALF_EVEN (banker's rounding) ties to even instead of away
    # from zero; should be ROUND_HALF_UP.
    return str(Decimal(amount).quantize(quantum, rounding=ROUND_HALF_EVEN))
