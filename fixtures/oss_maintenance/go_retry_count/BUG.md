# Bug report: `Do` gives up one attempt early (and never calls fn when attempts==1)

`retry.Do(attempts, fn)` should call `fn` up to `attempts` times, stopping at
the first success, and invoke `fn` **exactly once per attempt**. A user reports
two related failures:

```
calls := 0
err := retry.Do(3, func() error {
    calls++
    if calls < 3 { return errors.New("transient") }
    return nil
})
// got:  err = "transient", calls = 2
// want: err = nil,         calls = 3
```

With `attempts == 1`, `fn` is never called at all and `Do` returns `nil` as if
it had succeeded.

Expected: `Do` runs `fn` exactly `attempts` times in the worst case, returns
`nil` on the first success and the last error if all attempts fail. `attempts <
1` returns `ErrNoAttempts` and never calls `fn`.

You are the maintainer. Reproduce, fix the root cause minimally (keep the `Do`
signature and `ErrNoAttempts`), and **leave behind a regression test**.
