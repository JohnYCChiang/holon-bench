# Self-bootstrap fixture: retry/repair policy

`engine.py` is a frozen retry simulator. It replays a run *trace* (a list of
attempt outcomes) under a `policy.json`:

```
simulate(policy, trace) -> {"converged": bool, "attempts_used": int}
```

Each outcome is either `"pass"` or a failure-class string. An attempt that fails
with a class listed in `policy.retryable_failures` is retried (up to
`policy.max_attempts`); any other failure stops the run.

`failed_run.json` is a recorded run that never converged. Diagnose why from the
trace and fix `policy.json` so the run converges — without making genuinely fatal
failures retryable and without removing the attempt budget.

You may only edit `policy.json`. Do not edit `engine.py`, `failed_run.json`, or any test.
