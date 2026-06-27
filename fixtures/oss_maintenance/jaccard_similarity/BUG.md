# Bug report: `jaccard` reports too-low similarity for overlapping sets

`jaccard(a, b)` is documented to return the Jaccard similarity of two inputs
treated as sets: `|a & b| / |a | b|`. A user reports the score is wrong whenever
the inputs overlap:

```
jaccard(["a", "b"], ["b", "c"])   # got 0.25, want 0.3333...
```

The intersection `{b}` has size 1 and the true union `{a, b, c}` has size 3, so
the answer should be `1/3`. The implementation computes the denominator as
`len(a) + len(b)`, which double-counts the shared element (and miscounts
duplicates) instead of using the size of the union.

Expected: the denominator is the number of distinct elements in either input.
Duplicates within an input are ignored. Two empty inputs are identical, so
`jaccard([], [])` is `1.0` (not a division-by-zero crash).

You are the maintainer. Reproduce, fix the root cause with a minimal change, and
**leave behind a regression test** so this defect cannot come back.
