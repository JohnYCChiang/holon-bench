# Bug report: an escaped quote inside a string breaks bracket validation

`quote_balance::validate` checks that `()[]{}` are balanced, treating brackets
inside a double-quoted span as literal text. Inside a quoted span a backslash is
supposed to escape the next character, so `\"` is a literal quote, not the end
of the string. A user reports that escaped quotes corrupt the parse:

```
validate("\"\\\"\"")   // a string containing one escaped quote
// got:  Err(UnterminatedString)
// want: Ok(())
```

The in-string branch never handles the backslash escape, so the `\"` is read as
a closing quote and the following `"` re-opens a new (now unterminated) string.
Any input with an escaped quote (or an escaped backslash) is mis-parsed.

Expected: inside a quoted span a backslash escapes the next character, so escaped
quotes and backslashes are consumed literally and the surrounding bracket
validation stays correct.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`validate` signature and `QuoteError` variants), and **leave behind a regression
test**.
