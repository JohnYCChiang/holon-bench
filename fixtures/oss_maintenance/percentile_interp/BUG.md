# Bug report: percentile is off -- median of an even list is wrong

`percentile(data, p)` is documented to return the `p`-th percentile using
**linear interpolation between closest ranks** (the common "linear" method,
rank = `p/100 * (n - 1)`). A user reports the median is wrong:

```
percentile([1, 2, 3, 4], 50)
# got:  3.0
# want: 2.5
```

The rank is being computed as `p/100 * n` and then truncated to an integer
index with no interpolation, so it lands on the wrong element.

Expected: rank = `p/100 * (n - 1)`; interpolate linearly between the two
bracketing order statistics; `p = 0` returns the min and `p = 100` the max. An
empty list or `p` outside `[0, 100]` raises ValueError; the input is not
mutated.

You are the maintainer. Reproduce, fix the root cause with a minimal change,
and **leave behind a regression test** so this defect cannot come back.
