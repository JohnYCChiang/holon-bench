# Self-bootstrap fixture: quality gate thresholds

`engine.py` is a frozen quality gate. It reads `thresholds.json`, a map of
`metric -> minimum`, and rejects any submission whose metric falls below its
minimum:

```
gate(thresholds, metrics) -> "accept" | "reject"
```

Metrics absent from the config are ungated (effectively a floor of 0).

Coverage is currently ungated, so submissions with high scores but poor coverage
slip through. Add a `coverage` floor of `0.80` while keeping the existing score
bar (`70`). Do not over-tighten: a submission exactly at both bars must pass.

You may only edit `thresholds.json`. Do not edit `engine.py` or any test.
