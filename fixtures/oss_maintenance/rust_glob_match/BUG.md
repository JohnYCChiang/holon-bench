# Bug report: trailing `*` fails to match an empty suffix

`glob_match::matches(pattern, text)` supports `*` (any run, including empty) and
`?` (exactly one character). A user reports a pattern that should clearly match
coming back false:

```
matches("a*", "a")   // got false, want true
```

In the matcher, the `*` branch bails out as soon as the remaining text is empty,
so `*` is effectively "one or more" instead of "zero or more". Any pattern whose
`*` needs to match an empty run (commonly a trailing `*`) fails.

Expected: `*` matches zero or more characters (with proper backtracking), so
`matches("a*", "a")` and `matches("*", "")` are true, while `?` still matches
exactly one character.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`matches` signature and the `*`/`?` semantics), and **leave behind a regression
test**.
