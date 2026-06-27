# Self-bootstrap fixture: verifier severity map

`engine.py` is a frozen classifier. It reads `severity.json` (a map of
failure-tag -> level) and decides whether a submission is blocked:

```
classify(tags, severity_map) -> "block" | "allow"
```

A submission is `"block"`ed if any of its failure tags maps to `"critical"`.
Tags that are absent from the map, or map to `"warning"`, do not block.

A new failure mode, `state_sync_corruption`, has been observed in production and
must be treated as `critical`. Extend `severity.json` so it blocks — without
downgrading any tag that is already `critical`.

You may only edit `severity.json`. Do not edit `engine.py` or any test.
