# Self-bootstrap fixture: approval quorum rules

`engine.py` is a frozen approval engine. It reads `quorum.json` (per-change-type
rules, with a `default_rule` fallback) and decides whether a change has quorum:

```
is_approved(config, change) -> bool
```

A rule is `{"min_approvals": int, "required_roles": [role, ...], "allow_self_approval": bool}`.
When `allow_self_approval` is false, approvals whose `user` equals the change `author`
are ignored. A change is approved only if enough eligible approvals remain AND every
required role appears among them.

The sensitive `prod_db_migration` change type has no rule, so it falls back to the
permissive default (one approval is enough). Add a `prod_db_migration` rule that
requires at least 2 approvals, requires both a `dba` and a `security` approval, and
forbids self-approval. Do not weaken the existing `code_change` rule.

You may only edit `quorum.json`. Do not edit `engine.py` or any test.
