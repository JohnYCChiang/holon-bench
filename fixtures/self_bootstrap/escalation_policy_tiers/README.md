# Self-bootstrap fixture: tiered escalation policy

`engine.py` is a frozen escalation engine. It reads `escalation.json`, a list of
thresholds, and returns the action for the *highest* threshold whose
`min_failures` is at or below the observed failure count:

```
escalate(policy, failures) -> action
```

Below the lowest threshold it returns `default_action`.

A new top tier is required: at **five** consecutive failures the policy must
return `"page_oncall"`. Add that tier without lowering or removing the existing
`retry` (>=1) and `notify_team` (>=3) tiers, and make sure it does not fire
before five failures.

You may only edit `escalation.json`. Do not edit `engine.py` or any test.
