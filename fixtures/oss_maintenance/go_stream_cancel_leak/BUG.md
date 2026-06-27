# Bug report: producer goroutine leaks when the caller stops reading

`worker.Stream(ctx, n)` returns a channel that a producer goroutine fills with
`0..n-1`. Callers are allowed to stop reading early (typically on context
cancellation). A service owner reports that goroutines pile up under load:

```
# pprof goroutine dump (steady state, after thousands of cancelled requests)
goroutine profile: total 4123
4096 @ 0x... worker.Stream.func1   <-- stuck on channel send, never returns
```

The producer blocks forever on `out <- i` once the caller stops receiving, and
it ignores `ctx`. When the context is cancelled the producer must stop and the
goroutine must exit.

You are the maintainer. Reproduce the leak, fix the root cause minimally (keep
`Stream`'s signature and the in-order delivery contract), and **leave a
regression test** behind.
