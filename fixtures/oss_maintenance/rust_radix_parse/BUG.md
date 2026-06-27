# Bug report: `parse_radix` panics on a sign or a bad digit and ignores overflow

`parse_radix(s, radix) -> Result<i64, ParseError>` parses an integer written in
the given `radix` (2..=36), allowing an optional leading `+`/`-` and
case-insensitive digits. The contract says malformed input is reported as an
`Err` and the function **must never panic**. A user reports a crash:

```
thread 'main' panicked at 'called `Option::unwrap()` on a `None` value'
// parse_radix("-101", 2)  -> expected Ok(-5)
```

`to_digit(radix).unwrap()` panics on the sign character (and on any non-digit),
and the running total can overflow `i64` silently.

Expected: a leading `+`/`-` is honored; a non-digit returns
`Err(ParseError::InvalidDigit(c))`; empty input (or only a sign) returns
`Err(ParseError::Empty)`; `radix` outside `2..=36` returns
`Err(ParseError::BadRadix)`; overflow returns `Err(ParseError::Overflow)`.
Never panic.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`parse_radix` signature and the `ParseError` variants), and **leave behind a
regression test**.
