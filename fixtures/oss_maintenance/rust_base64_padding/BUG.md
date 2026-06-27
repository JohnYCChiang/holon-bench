# Bug report: base64 `encode` drops the `=` padding

This crate implements standard (RFC 4648) base64. `encode(data)` should always
emit `=` padding so the output length is a multiple of four. A user reports the
padding missing for inputs whose length is not a multiple of three:

```
encode(b"M")    // got "TQ",  want "TQ=="
encode(b"Ma")   // got "TWE", want "TWE="
```

For a short trailing chunk the implementation simply omits the final one or two
output characters instead of writing them as `=`.

Expected: a full 3-byte chunk encodes to four characters with no padding; a
2-byte tail gets one `=`; a 1-byte tail gets two `=`; `encode(b"")` is `""`. The
standard test vectors (`f` -> `Zg==`, `fo` -> `Zm8=`, `foo` -> `Zm9v`, ...) hold.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`encode(&[u8]) -> String` signature), and **leave behind a regression test**.
