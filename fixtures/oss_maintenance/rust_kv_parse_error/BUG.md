# Bug report: `parse_kv` panics instead of returning an error

`parse_kv(line: &str) -> Result<(String, String), ParseError>` parses a
`key=value` line. The contract:

- split on the **first** `=`, so the value may itself contain `=`,
- return `Err(ParseError::MissingDelimiter)` when there is no `=`,
- return `Err(ParseError::EmptyKey)` when the key is empty,
- **never panic** — malformed input is reported as an `Err`.

A user reports a crash on a line with no `=`:

```
thread 'main' panicked at 'called `Option::unwrap()` on a `None` value', src/lib.rs:18
```

```
parse_kv("noeq")   // got: panic;  want: Err(ParseError::MissingDelimiter)
```

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`parse_kv` signature, the `ParseError` variants, and the first-`=` split so
values may contain `=`), and **leave behind a regression test** that pins the
error path.
