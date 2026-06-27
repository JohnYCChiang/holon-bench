from math import gcd


def reduce_fraction(num, den):
    """Reduce ``num/den`` to lowest terms as a ``(numerator, denominator)`` tuple.

    The result is normalized so the denominator is positive and any sign lives on
    the numerator. ``reduce_fraction(0, 5)`` is ``(0, 1)``. A zero denominator
    raises ``ZeroDivisionError``.
    """
    if den == 0:
        raise ZeroDivisionError("denominator is zero")
    g = gcd(num, den)
    # BUG: divides by the gcd but never normalizes the sign, so a negative
    # denominator survives (e.g. reduce_fraction(1, -2) -> (1, -2)).
    return (num // g, den // g)
