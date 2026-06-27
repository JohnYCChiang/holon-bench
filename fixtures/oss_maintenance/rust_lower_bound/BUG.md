# Bug report: `lower_bound` returns the position AFTER a duplicated value

`lower_bound(a, target)` should return the index of the first element of the
ascending-sorted slice `a` that is `>= target` (equivalently, the number of
elements strictly less than `target`, i.e. the leftmost insertion point). A user
reports the wrong index when `target` appears more than once:

```
lower_bound(&[1, 2, 2, 2, 3], 2)
// got:  4   want: 1   (index of the FIRST 2)
```

The binary search advances on `a[mid] <= target`, which finds the position
after the last equal element (an upper bound) instead of the first.

Expected: for a duplicated target, return the index of its first occurrence; for
an absent target, return the insertion point that keeps `a` sorted. `a` is
sorted ascending.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`lower_bound` signature), and **leave behind a regression test**.
