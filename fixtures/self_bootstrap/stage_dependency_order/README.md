# Self-bootstrap fixture: stage dependency ordering

`engine.py` is a frozen scheduler. It reads `pipeline.json` (a map of
`stage -> [stages it needs]`) and produces a deterministic topological order:

```
resolve_order(pipeline) -> [stage, ...]   # raises on a cycle or unknown dep
```

Among ready stages it picks the lowest name, so `deploy` currently runs before
`integration_test` (both only need `build`) — an unsafe ordering.

Add the missing dependency so `deploy` runs *after* `integration_test`, without
removing existing dependencies, introducing a cycle, or depending on stages that
do not exist.

You may only edit `pipeline.json`. Do not edit `engine.py` or any test.
