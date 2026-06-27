# Bug report: touching intervals are not merged

`merge(intervals)` is documented to return the sorted, minimal set of
non-overlapping intervals, merging any intervals that **overlap or touch**
(share an endpoint). A user reports that adjacent intervals are left split:

```
merge([[1, 2], [2, 3]])
# got:  [[1, 2], [2, 3]]
# want: [[1, 3]]
```

Intervals that merely touch at an endpoint (end == next start) should collapse
into one interval, but they come back separate.

Expected: overlapping or touching intervals merge; the result is sorted by
start, has no element lost, and the input is not mutated. An interval with
start > end raises ValueError.

You are the maintainer. Reproduce, fix the root cause with a minimal change,
and **leave behind a regression test** so this defect cannot come back.
