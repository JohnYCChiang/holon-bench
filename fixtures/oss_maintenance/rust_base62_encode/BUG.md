# Bug report: `encode` returns base62 strings in reverse

`base62_codec::encode(n: u64) -> String` encodes an integer with the alphabet
`0-9 A-Z a-z`, most-significant digit first. A user reports the output is
backwards for any multi-digit number:

```
encode(62)    // got "01", want "10"
encode(3844)  // got "001", want "100"
```

The digits are generated least-significant first (by repeatedly taking
`n % 62`), but the buffer is never reversed before being turned into the string,
so every multi-digit result is mirrored. Single-digit values happen to look
correct, which hid the defect.

Expected: the encoded string reads most-significant digit first, e.g.
`encode(62) == "10"`, and `encode(0) == "0"`.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`encode` signature and the alphabet), and **leave behind a regression test** that
pins the digit order.
