# Bug report: `reduce_fraction` leaves the sign on the denominator

`reduce_fraction(num, den)` reduces a fraction to lowest terms and returns a
`(numerator, denominator)` tuple. The contract says the denominator is always
positive, with any sign carried by the numerator. A user reports a negative
denominator leaking through:

```
reduce_fraction(1, -2)    # got (1, -2), want (-1, 2)
reduce_fraction(3, -6)    # got (1, -2), want (-1, 2)
reduce_fraction(-1, -3)   # got (-1, -3), want (1, 3)
```

The implementation divides both parts by their gcd but never normalizes the
sign, so a negative denominator survives.

Expected: the reduced denominator is positive; the numerator carries the sign;
`reduce_fraction(0, 5)` and `reduce_fraction(0, -5)` are both `(0, 1)`; a zero
denominator raises `ZeroDivisionError`.

You are the maintainer. Reproduce, fix the root cause with a minimal change, and
**leave behind a regression test** so this defect cannot come back.
