# Self-bootstrap fixture: command alias redirects

`engine.py` is a frozen alias resolver. It reads `aliases.json` (a `name -> target`
map) and follows the chain until it reaches a terminal name that is not itself an
alias, raising on a cycle:

```
resolve(aliases, name) -> canonical_name
```

The `deploy` alias must resolve to the canonical `release_v2`, but its chain dead-ends
at `ship`. Add the missing hop so `deploy -> ship -> release -> release_v2`. Do not
repoint `deploy` straight to `release_v2` (the indirection through `ship` is intentional),
do not repoint the existing `release` alias, and do not introduce a cycle.

You may only edit `aliases.json`. Do not edit `engine.py` or any test.
