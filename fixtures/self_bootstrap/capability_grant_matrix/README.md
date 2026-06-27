# Self-bootstrap fixture: capability grant matrix

`engine.py` is a frozen authorizer. It reads `capabilities.json`, a matrix of
`role -> [allowed actions]`, and decides each request:

```
authorize(matrix, role, action) -> "allow" | "deny"
```

A request is allowed only when the action is listed under that exact role.

The `maintainer` role now owns pull-request merges but is missing the `merge_pr`
grant. Add it for `maintainer` only — do not grant it to lower-privilege roles
(e.g. `guest`) and do not revoke any existing grant.

You may only edit `capabilities.json`. Do not edit `engine.py` or any test.
