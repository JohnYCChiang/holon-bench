# Self-bootstrap fixture: task routing table

`engine.py` is a frozen dispatcher. It reads `routing.json` and maps a task type
to the worker that handles it:

```
dispatch(routing, task_type) -> worker name | routing["default"]
```

A task type with no explicit route falls through to `routing["default"]`
(currently `"unrouted"`, meaning *dropped*).

`schema_migration` submissions are being dropped because the table has no route
for them. Add an explicit route so they reach `"migration_worker"`, without
repointing existing routes and without hijacking the default sink (every other
unknown task type must still fall through to `"unrouted"`).

You may only edit `routing.json`. Do not edit `engine.py` or any test.
