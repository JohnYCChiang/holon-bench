# Bug report: `Difference` returns the wrong elements

`setops.Difference(a, b)` should return the elements of `a` that are **not**
present in `b`, preserving `a`'s first-seen order and collapsing duplicates. A
user reports it returns exactly the elements it should have removed:

```
Difference([]string{"a", "b", "c"}, []string{"b"})
// got:  ["b"]
// want: ["a", "c"]
```

The membership test is inverted: it keeps the elements found in `b` instead of
dropping them.

Expected: keep `a`'s elements not in `b`, in order, de-duplicated; when nothing
remains return an empty (non-nil) slice; inputs are not mutated.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`Difference(a, b []string) []string` signature), and **leave behind a
regression test**.
