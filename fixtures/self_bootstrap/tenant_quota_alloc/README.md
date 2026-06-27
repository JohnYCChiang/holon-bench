# Self-bootstrap fixture: tenant quota allocation

`engine.py` is a frozen quota accountant. It reads `quotas.json` (a per-tenant
allocation plus a `total_capacity`) and exposes:

```
quota_for(config, tenant) -> int            # 0 when the tenant is unlisted
is_overcommitted(config) -> bool            # sum(tenants) > total_capacity
```

The new tenant `tenant_c` has no allocation, so it is starved (quota 0). Give it
a quota of at least 20 without over-committing the pool (`total_capacity` is 100)
and without reducing the existing `tenant_a` (40) or `tenant_b` (30) allocations.
Do not inflate `total_capacity`.

You may only edit `quotas.json`. Do not edit `engine.py` or any test.
