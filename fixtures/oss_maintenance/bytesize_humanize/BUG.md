# Bug report: `humanize` prints "1024.0 KiB" instead of rolling over to MiB

`humanize.humanize(n)` formats a byte count with binary units and one decimal
place. A user reports an impossible-looking unit:

```
>>> from src.humanize import humanize
>>> humanize(1048555)
'1024.0 KiB'        # expected '1.0 MiB'
```

`1048555` bytes is `1023.98... KiB`, which the unit loop correctly keeps in KiB.
But formatting to one decimal place **rounds it up to `1024.0`**, and the code
prints that as-is instead of recognizing it has reached the next unit and
rolling over to `1.0 MiB`. The same happens at every unit boundary just below a
power of 1024.

Expected: when rounding to one decimal place reaches 1024.0, the value rolls over
to the next larger unit (e.g. `1.0 MiB`), so no output ever reads `1024.0 <unit>`.

You are the maintainer. Reproduce, fix the root cause minimally (keep the
`humanize(n)` API and one-decimal formatting), and **leave behind a regression
test** that pins the rounding roll-over.
