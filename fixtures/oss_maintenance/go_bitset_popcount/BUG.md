# Bug report: `PopCount` ignores the high 32 bits

`bitset.PopCount(x uint64) int` is documented to return the number of set bits
in a 64-bit value. A user reports set bits going uncounted:

```
PopCount(1 << 40)   // got 0, want 1
PopCount(^uint64(0)) // got 32, want 64
```

The loop only iterates over bit positions `0..31`, so any bit set in the upper
half of the word is never inspected.

Expected: every one of the 64 bit positions is counted; `PopCount(0)` is `0` and
`PopCount(^uint64(0))` is `64`.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`PopCount(x uint64) int` signature), and **leave behind a regression test**.
