# Bug report: round-trip corrupts runs of 10 or more identical characters

`rle.encode` / `rle.decode` are an inverse pair: `decode(encode(x)) == x` for any
string. A user reports the round-trip breaks once a run reaches length 10:

```
>>> from src.rle import encode, decode
>>> encode("a" * 12)
'a12'
>>> decode("a12")
Traceback (most recent call last):
  ...
IndexError: string index out of range
```

`encode` correctly writes the multi-digit count `12`, but `decode` only ever reads
a **single digit** for the run length, so any run of 10+ characters is decoded
wrong (or crashes). Runs of 1–9 happen to work, which is why this slipped through.

Expected: `decode` reads the full (possibly multi-digit) decimal run length, so the
round-trip is exact for runs of any length.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`encode`/`decode` API), and **leave behind a regression test** that pins the
multi-digit round-trip.
