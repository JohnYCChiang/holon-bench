# Bug report: `distance` miscounts edits for non-ASCII strings

`distance(a, b)` returns the Levenshtein edit distance between two strings,
counted in characters. A user reports an inflated distance whenever the inputs
contain multibyte characters:

```
distance("café", "cafe")   // got 2, want 1
```

`é` is a single character but two UTF-8 bytes. The implementation indexes the raw
byte slices (`a.as_bytes()`), so a multibyte character is treated as several
positions and counts as several edits.

Expected: edits are counted over Unicode scalar values (`char`s); a single
multibyte character — even a 4-byte emoji — is one edit. The classic ASCII cases
(`kitten` -> `sitting` is 3, `flaw` -> `lawn` is 2) still hold.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`distance(&str, &str) -> usize` signature), and **leave behind a regression test**.
