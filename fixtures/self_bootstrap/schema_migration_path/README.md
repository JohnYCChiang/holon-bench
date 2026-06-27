# Self-bootstrap fixture: schema version migration map

`engine.py` is a frozen migration planner. It reads `migrations.json` (a list of
directed `{"from", "to"}` steps) and finds the shortest version path:

```
find_path(migrations, start, end) -> [version, ...] | None
```

The map has two disconnected islands — `v1 -> v2` and `v3 -> v4` — so there is no
way to migrate `v1` data forward to `v4`.

Bridge the gap so `v1` can reach `v4` *through every intermediate version*
(`v1 -> v2 -> v3 -> v4`). Add only the missing `v2 -> v3` step. Do not add a
data-unsafe direct shortcut (e.g. `v1 -> v4` or `v2 -> v4`) and do not drop the
existing steps.

You may only edit `migrations.json`. Do not edit `engine.py` or any test.
