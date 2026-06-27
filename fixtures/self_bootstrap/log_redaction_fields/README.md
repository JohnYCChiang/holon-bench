# Self-bootstrap fixture: log redaction

`engine.py` is a frozen log redactor. It reads `redaction.json` (which lists the
field names that must be masked) and replaces those fields' values with `***`:

```
redact(config, record) -> dict   # masked copy of record
```

Fields not in the list are left untouched. The `ssn` field is leaking into logs
because it is not on the list. Add `ssn` to `redact_fields` without redacting
everything: non-sensitive fields like `username` must stay visible, and the
existing `password` / `api_key` masking must be preserved.

You may only edit `redaction.json`. Do not edit `engine.py` or any test.
