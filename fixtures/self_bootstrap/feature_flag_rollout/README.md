# Self-bootstrap fixture: feature-flag rollout

`engine.py` is a frozen feature-flag evaluator. It reads `flags.json` (a map of
`flag -> rule`) and decides whether a flag is on for a given user:

```
is_enabled(flags, flag, user_id) -> bool
```

A rule is `{"enabled": bool, "rollout_percent": int, "allowlist": [user_id, ...]}`.
A user sees the flag if the flag is enabled AND (the user is allowlisted OR their
deterministic rollout bucket is below `rollout_percent`).

The `internal_metrics` flag must be visible to the internal user `ops_admin`, but
it must NOT begin a percentage rollout to customers (keep `rollout_percent` at 0).
Add `ops_admin` to the allowlist. Do not flip the flag on globally.

You may only edit `flags.json`. Do not edit `engine.py` or any test.
