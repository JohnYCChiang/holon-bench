# Self-bootstrap fixture: review pipeline definition

`engine.py` is a small, frozen workflow engine. It loads `workflow.json` and
evaluates a *submission record* against the pipeline:

```
evaluate(workflow, submission) -> "accept" | "reject"
```

A submission is `"accept"`ed only when **every gate of every stage** is truthy in
the record. Available gate keys a stage may require:

- `compiles`
- `tests_pass`
- `scope_pass`
- `hidden_pass`   — the hidden regression suite passed
- `mutation_pass` — the mutation suite passed

You may only edit `workflow.json`. Do not edit `engine.py` or any test.
