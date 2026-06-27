# Bug report: `roman_to_int` ignores subtractive notation

`roman_to_int(s)` converts an uppercase Roman numeral to an integer. A user
reports that subtractive pairs are computed wrong:

```
roman_to_int("IV")   # got 6, want 4
roman_to_int("IX")   # got 11, want 9
roman_to_int("MCMXCIV")  # got 2106, want 1994
```

The implementation adds every symbol's value unconditionally, so a smaller
symbol placed before a larger one (e.g. `I` before `V`) is added instead of
subtracted.

Expected: subtractive pairs (`IV`, `IX`, `XL`, `XC`, `CD`, `CM`) reduce the
total; ordinary additive numerals still sum. An empty string is `0`; a character
outside `IVXLCDM` raises `ValueError`.

You are the maintainer. Reproduce, fix the root cause with a minimal change, and
**leave behind a regression test** so this defect cannot come back.
