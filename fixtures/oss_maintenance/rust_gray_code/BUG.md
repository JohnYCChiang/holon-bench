# Bug report: `gray_decode` does not invert `gray_encode`

This crate implements binary-reflected Gray code. `gray_encode(n)` maps an
ordinal to its Gray code and `gray_decode(g)` is documented as the exact inverse,
so `gray_decode(gray_encode(n)) == n` for every `u32`. A user reports the
round-trip failing:

```
gray_encode(5)            // 7
gray_decode(7)            // got 4, want 5
```

Decoding a Gray code requires folding in every higher bit (XOR the running value
with each successive right shift until no bits remain). The implementation does a
single `g ^ (g >> 1)`, which only undoes one reflection level.

Expected: `gray_decode` inverts `gray_encode` for all values, including
high-order ones; `gray_decode(0) == 0`.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`gray_encode` / `gray_decode` signatures), and **leave behind a regression test**.
