# Examples

This directory contains minimal runnable sample cases to help you add your own OSS repository as a Holon-Bench case.

## Included Examples

| Directory | Language | What It Demonstrates |
|---|---|---|
| [`minimal-python-case/`](minimal-python-case/) | Python | The simplest possible case: one function, one test, one verifier |

## How to Add Your Own Case

1. **Copy the minimal example** and rename it to match your case ID.
2. **Edit `case.yaml`** — fill in `id`, `track`, `user_request`, `allowed_paths`, `forbidden_paths`, and `verifier.commands`.
3. **Put your fixture files** in `fixture/` — this is the workspace the agent will see.
4. **Add your case** to the appropriate track YAML in `cases/`.
5. **Run schema check** to validate:

```bash
python3 runners/schema_check.py .
```

See the full case schema at [`schemas/case.schema.json`](../schemas/case.schema.json).
