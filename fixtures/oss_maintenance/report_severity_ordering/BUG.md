# Bug report: high-severity findings sort below lower-severity ones

`render_report` is supposed to list findings with the **highest severity first**,
breaking ties by name (ascending). A user reports that a severity-`10` finding
shows up *below* a severity-`9` finding:

```
$ render_report([{ "name": "disk", "severity": 9 }, { "name": "auth", "severity": 10 }])
['9:disk', '10:auth']      # WRONG — 10 is more severe than 9 and must come first
```

Expected output: `['10:auth', '9:disk']`.

Severity is an integer and must be ordered numerically, not lexicographically.

You are the maintainer. Reproduce, fix the root cause minimally, and **leave a
regression test** behind so multi-digit severities stay ordered correctly.
