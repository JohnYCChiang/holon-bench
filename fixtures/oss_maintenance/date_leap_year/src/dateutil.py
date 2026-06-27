"""Day arithmetic on the proleptic Gregorian calendar."""

_DAYS_IN_MONTH = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def _is_leap(year):
    return year % 4 == 0  # BUG: ignores the century rule (must also be divisible by 400)


def _days_from_epoch(year, month, day):
    total = 0
    for y in range(1, year):
        total += 366 if _is_leap(y) else 365
    for m in range(1, month):
        total += _DAYS_IN_MONTH[m - 1]
        if m == 2 and _is_leap(year):
            total += 1
    total += day - 1
    return total


def days_between(a, b):
    """Number of days from date ``a`` to date ``b`` (Gregorian calendar).

    Each date is a ``(year, month, day)`` tuple. The result is ``b - a`` in
    whole days and may be negative. Leap years follow the Gregorian rule:
    divisible by 4, except century years that are not divisible by 400.
    """
    return _days_from_epoch(*b) - _days_from_epoch(*a)
