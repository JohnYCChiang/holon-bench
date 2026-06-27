# Bug report: `decode_hex` panics on odd-length or non-hex input

`decode_hex(s: &str) -> Result<Vec<u8>, HexError>` decodes an ASCII hex string
into bytes (two hex digits per byte, high nibble first, upper- or lower-case).
The contract says malformed input is reported as an `Err` and the function
**must never panic**. A user reports a crash:

```
thread 'main' panicked at 'index out of bounds: the len is 3 but the index is 3'
// decode_hex("abc")  -> expected Err(HexError::OddLength)
```

An odd-length string walks past the end of the buffer, and a non-hex character
makes `to_digit(16).unwrap()` panic instead of returning an error.

Expected: odd length returns `Err(HexError::OddLength)`; a non-hex character
returns `Err(HexError::InvalidChar(c))`; valid input round-trips. Never panic.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`decode_hex` signature and the `HexError` variants), and **leave behind a
regression test**.
