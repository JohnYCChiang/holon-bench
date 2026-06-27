# Bug report: rate limiter holds expired events one tick too long

`limiter.New(capacity, window)` admits at most `capacity` events within any
window of `window` ticks. An event recorded at time `t` is in-window at time
`now` while `now - t < window`; once `now - t >= window` it has expired and must
no longer count. A user reports requests being denied right at the window edge:

```
l := limiter.New(2, 10)
l.Allow(0)   // true
l.Allow(1)   // true
l.Allow(2)   // false (capacity full)
l.Allow(10)  // got: false   want: true  (event at t=0 is exactly 10 ticks old -> expired)
```

The pruning test keeps an event that is exactly `window` ticks old, so the
oldest slot never frees up on time and callers are throttled one tick too long.

Expected: an event exactly `window` ticks old has expired; only events with
`now - t < window` still occupy capacity. Times are non-decreasing; a denied
request is not recorded.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`New`/`Allow` API), and **leave behind a regression test**.
