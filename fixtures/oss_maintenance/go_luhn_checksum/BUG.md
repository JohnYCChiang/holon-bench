# Bug report: `Valid` rejects legitimate numbers (missing Luhn adjustment)

`luhn.Valid` checks a decimal string with the Luhn algorithm. A user reports a
genuinely valid number being rejected:

```
Valid("59")   // got false, want true
```

In Luhn, every second digit (counting from the right) is doubled, and **if the
doubled value is greater than 9 you subtract 9** (equivalently, sum its two
digits). The implementation doubles correctly but never applies that subtraction,
so any number where a doubled digit exceeds 9 is mis-scored.

Expected: a doubled digit greater than 9 contributes `doubled - 9`, so the
classic Luhn checks pass (e.g. `Valid("59")` and `Valid("79927398713")` are
true).

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`Valid(number)` signature), and **leave behind a regression test**.
