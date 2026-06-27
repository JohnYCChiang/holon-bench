# Bug report: `merge_k` drops every list's tail

`merge_k(lists)` merges k already-sorted `(key, tag)` lists into one ascending,
stable list using a binary min-heap. A user reports most of their data vanishing:

```
merge_k(vec![vec![(1, 0), (3, 0)], vec![(2, 1)]])
// got:  [(1, 0), (2, 1)]
// want: [(1, 0), (2, 1), (3, 0)]
```

The loop seeds the heap with each list's first element but, after popping an
element, never pushes the NEXT element of that same list. So every list
contributes only its head and the remaining elements are silently dropped.

Expected: every element survives exactly once; the output is ascending by key;
the merge is stable (for equal keys, earlier lists come first and a list's
original order is preserved).

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`merge_k(Vec<Vec<(i32, u32)>>) -> Vec<(i32, u32)>` signature and the stable
ordering), and **leave behind a regression test**.
