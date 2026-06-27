# Bug report: first page of results is missing, last items duplicated/shifted

`paginate(items, page_size, page)` is documented to return contiguous,
non-overlapping slices of `items` for a 1-based `page`. A user reports that
page 1 does **not** return the first items:

```
paginate(["a", "b", "c", "d", "e"], 2, 1)
# got:  ['c', 'd']
# want: ['a', 'b']
```

Every page is shifted forward by one page, so the first items can never be
read and a page past the data still returns rows that belong elsewhere.

Expected: page 1 returns the first `page_size` items, page 2 the next, and so
on; a page past the end returns an empty list.

You are the maintainer. Reproduce, fix the root cause with a minimal change,
and **leave behind a regression test** so this defect cannot come back.
