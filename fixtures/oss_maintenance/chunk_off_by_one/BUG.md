# Bug report: `chunk` silently drops the final partial batch

`chunk(seq, size)` is documented to split a sequence into consecutive lists of
length `size`, where the **last list may be shorter** when `len(seq)` is not an
exact multiple of `size`. A user reports the trailing elements just disappear:

```
>>> chunk([1, 2, 3, 4, 5], 2)
[[1, 2], [3, 4]]            # WRONG — the final [5] was dropped
```

Expected output: `[[1, 2], [3, 4], [5]]`.

No elements may be lost: concatenating the returned chunks must reproduce the
original sequence.

You are the maintainer. Reproduce, fix the root cause with a minimal change, and
**leave behind a regression test** so the trailing batch cannot vanish again.
