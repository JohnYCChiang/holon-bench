# Bug report: `Weekday` is off by one for January and February dates

`weekday.Weekday(year, month, day) string` returns the English day name for a
Gregorian date using Sakamoto's algorithm. A user reports January/February dates
landing on the wrong day:

```
Weekday(2000, 1, 1)   // got "Monday", want "Saturday"
Weekday(2024, 2, 29)  // wrong day
```

Sakamoto's method requires January and February to be counted as months of the
*previous* year (the leap-day adjustment). The implementation skips the
`if month < 3 { year-- }` step, so every Jan/Feb date is shifted by one weekday.

Expected: all dates resolve correctly; only January and February take the
previous-year adjustment, and March-onward dates are unchanged.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`Weekday(year, month, day) string` signature), and **leave behind a regression
test**.
