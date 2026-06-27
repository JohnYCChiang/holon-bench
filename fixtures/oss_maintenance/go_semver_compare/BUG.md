# Bug report: `Compare` orders versions lexically, so 1.10.0 < 1.9.0

`semver.Compare(a, b)` should compare two `"MAJOR.MINOR.PATCH"` versions
**numerically per field** and return `-1`, `0`, or `1`. A user reports that a
double-digit field sorts wrong:

```
Compare("1.10.0", "1.9.0")
// got:  -1   (treats "10" < "9")
// want:  1
```

Each field is being compared as a string instead of as a number, so `"10"`
sorts before `"9"` and `"01"` differs from `"1"`.

Expected: fields compare numerically (`1.10.0 > 1.9.0`, `1.01.0 == 1.1.0`); a
version that is not three non-negative integers returns a non-nil error.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`Compare(a, b) (int, error)` signature), and **leave behind a regression test**.
