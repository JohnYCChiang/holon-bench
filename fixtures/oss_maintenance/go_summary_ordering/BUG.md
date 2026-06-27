# Bug report: summary lines come out in the wrong order

`report.Summarize(events)` is documented to render one `"name=count"` line per
event, ordered by **count descending**, with ties broken by **name ascending**.
A user reports the order is inverted — the least important rows float to the top:

```
events := []report.Event{{Name: "a", Count: 1}, {Name: "c", Count: 3}, {Name: "b", Count: 3}}
report.Summarize(events)
// got:  [a=1 c=3 b=3]   // WRONG — ascending, and the c/b tie is not name-ordered
// want: [b=3 c=3 a=1]   // count desc, ties by name asc
```

Expected output: `[b=3 c=3 a=1]`. The input slice must not be mutated.

You are the maintainer. Reproduce, fix the ordering contract minimally (keep the
`Summarize` signature and `Event` type), and **leave behind a regression test**
that pins the count-desc / name-asc ordering.
