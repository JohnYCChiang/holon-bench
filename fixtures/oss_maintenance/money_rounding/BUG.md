# Bug report: invoice totals are rounded with banker's rounding, not half-up

`round_half_up(amount, ndigits)` is documented to round a decimal value to
`ndigits` places using **round-half-away-from-zero** (commercial rounding), the
mode finance requires. A user reports that exact halves round the wrong way:

```
round_half_up("2.5", 0)
# got:  "2"
# want: "3"

round_half_up("0.125", 2)
# got:  "0.12"
# want: "0.13"
```

The function is using Python's default banker's rounding (ties to even) instead
of rounding halves away from zero, so totals are understated.

Expected: ties round away from zero for positive and negative amounts
(`-0.125` -> `-0.13`); the result is a string with exactly `ndigits` decimal
places; `ndigits < 0` raises ValueError.

You are the maintainer. Reproduce, fix the root cause with a minimal change,
and **leave behind a regression test** so this defect cannot come back.
