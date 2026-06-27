# Domain: Subscription (bounded context)

Implement `src/subscription.py` to satisfy these rules.

## Subscription (aggregate root, state machine)
- Newly created in state `"trialing"` with an empty `events` list.
- Allowed transitions (any other transition is a domain error, `ValueError`, and
  must not change the state or append an event):
  - `activate()`: from `"trialing"` or `"past_due"` -> `"active"`; appends
    `"activated"`.
  - `mark_past_due()`: from `"active"` -> `"past_due"`; appends `"past_due"`.
  - `cancel()`: from any non-terminal state -> `"canceled"`; appends `"canceled"`.
- `"canceled"` is terminal: every transition out of it is rejected.

Only edit `src/subscription.py`.
