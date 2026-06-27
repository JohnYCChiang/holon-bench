# Bug report: `Dedup` only removes back-to-back duplicates

`dedup.Dedup` is documented to remove duplicates while keeping the **first**
occurrence of each value in input order. A user reports duplicates surviving when
they are not adjacent:

```
Dedup([]string{"a", "b", "a", "c", "b"})
// got:  [a b a c b]
// want: [a b c]
```

The implementation only compares each element to its immediate predecessor (like
the Unix `uniq` tool), so a repeat that is not directly adjacent slips through.

Expected: every value appears once, in first-seen order, regardless of where the
duplicates occur. The result stays non-nil (empty, non-nil for empty input).

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`Dedup` signature and first-seen order), and **leave behind a regression test**.
