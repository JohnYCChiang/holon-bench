# Self-bootstrap fixture: circuit-breaker threshold

`engine.py` is a frozen circuit-breaker simulator. It replays a recorded sequence
of outcomes (`"ok"` / `"fail"`) under `breaker.json` and reports whether the breaker
ever tripped (reached `failure_threshold` consecutive failures):

```
replay(config, outcomes) -> {"tripped": bool, "max_consecutive": int}
```

A recorded run (`failed_run.json`) tripped the breaker even though its failures were
isolated blips — the longest failure streak is only 2. The `failure_threshold` is
set too low (2). Raise it just enough that the recorded run does NOT trip, while
keeping it finite so a genuinely failing service (a long failure streak) still trips.
Do not change the recorded run.

You may only edit `breaker.json`. Do not edit `engine.py`, `failed_run.json`, or any test.
