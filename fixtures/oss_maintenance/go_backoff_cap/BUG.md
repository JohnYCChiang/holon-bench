# Bug report: exponential backoff is never capped and overflows

`backoff.New(base, max)` builds an exponential backoff and `Delay(attempt)`
should return `min(base * 2^(attempt-1), max)` for a 1-based `attempt`. A user
reports the delay blows past `max` and eventually goes negative:

```
b := backoff.New(100, 1000)
b.Delay(5)
// got:  1600   (and Delay(60) wraps to a negative int64)
// want: 1000
```

The doubling loop never compares against `max`, so the value grows without
bound and overflows `int64` for large attempts.

Expected: the delay never exceeds `max`, never overflows, and is
non-decreasing in `attempt`; `Delay(1) == base`; an `attempt < 1` is treated as
the first attempt (returns `base`).

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`New`/`Delay` API), and **leave behind a regression test**.
