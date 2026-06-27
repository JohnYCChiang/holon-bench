# Bug report: `AddMinutes` returns a negative minute-of-day

`clock.AddMinutes(minuteOfDay, delta)` adds `delta` minutes to a time of day and
must return a minute-of-day in `[0, 1440)`, wrapping around midnight. A user
reports a negative result when subtracting across midnight:

```
AddMinutes(10, -20)
// got:  -10
// want: 1430   (00:10 minus 20 minutes = 23:50 the previous day)
```

In Go the `%` operator keeps the sign of the dividend, so `(10 + -20) % 1440`
is `-10`, not `1430`. Any computation that crosses midnight backwards returns a
negative, out-of-range value.

Expected: the result is normalized into `[0, 1440)` for any `delta` (including
deltas more negative than a full day).

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`AddMinutes` signature), and **leave behind a regression test**.
