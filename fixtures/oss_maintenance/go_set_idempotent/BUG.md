# Bug report: re-adding a value duplicates it in an "ordered set"

`registry.Set` is documented as an **insertion-ordered set**: `Add` is
idempotent, so adding a value that is already present is a no-op, and `Items`
returns each distinct value once in first-insertion order. A user reports
duplicates leaking through:

```
s := registry.New()
s.Add("a")
s.Add("b")
s.Add("a")        // already present -> should be a no-op
fmt.Println(s.Items())
// got:  [a b a]
// want: [a b]
```

Re-adding an existing value must not change the contents or the order.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`Set`/`New`/`Add`/`Items` API), and **leave behind a regression test** so the
idempotency contract is enforced.
