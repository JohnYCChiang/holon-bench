# Bug report: day counts are wrong around century years

`days_between(a, b)` returns the number of days from date `a` to date `b`
(each a `(year, month, day)` tuple, Gregorian calendar). A user reports the
count is off by a day whenever the span crosses a century year such as 1900:

```
days_between((1900, 2, 28), (1900, 3, 1))
# got:  2
# want: 1   # 1900 is NOT a leap year, so there is no Feb 29
```

1900 is divisible by 4 but is a century year not divisible by 400, so under the
Gregorian rule it is **not** a leap year. The code treats every year divisible
by 4 as a leap year, inserting a phantom Feb 29.

Expected: leap years follow the Gregorian rule (divisible by 4, except century
years which must also be divisible by 400). Note 2000 IS a leap year.

You are the maintainer. Reproduce, fix the root cause with a minimal change,
and **leave behind a regression test** so this defect cannot come back.
