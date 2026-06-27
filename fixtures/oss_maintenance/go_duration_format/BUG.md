# Bug report: `Format` shows total minutes instead of minutes-in-the-hour

`durfmt.Format(seconds int) string` renders a non-negative seconds count as
`<H>h<M>m<S>s`, where minutes and seconds are each `0..59` and hours carry the
remainder. A user reports a minutes overflow:

```
Format(3661)   // got "1h61m1s", want "1h1m1s"
```

The minutes component is computed as `seconds / 60` (the *total* minutes) rather
than `(seconds / 60) % 60` (the minutes within the current hour).

Expected: minutes and seconds wrap at 60; the hours component carries any whole
hours and does NOT wrap (e.g. `Format(86400)` is `"24h0m0s"`).

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`Format(seconds int) string` signature), and **leave behind a regression test**.
