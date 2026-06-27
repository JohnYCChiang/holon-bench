# Domain: Retry Budget / Circuit Breaker (bounded context)

Implement `src/retry.py`. A `RetryBudget` is an authoritative circuit breaker
driven by a monotonic logical clock.

## RetryBudget (aggregate root)
- Created with positive integers `max_failures` and `cooldown` (`ValueError`).
- State starts `"CLOSED"` with `failures == 0`, `opened_at is None`, `clock == 0`,
  and an empty `events` list.
- States: `"CLOSED"`, `"OPEN"`, `"HALF_OPEN"`.
- `allow(now)` is a pure query (no mutation):
  - returns `False` when state is `"OPEN"` and `now < opened_at + cooldown`;
  - otherwise returns `True` (a cooled-down breaker permits one trial).
- `record_success(now)` and `record_failure(now)` both:
  - Invariant: `now` must be `>= clock` (monotonic); otherwise `ValueError` with
    no mutation.
  - If state is `"OPEN"` and `now >= opened_at + cooldown`, the breaker first
    lazily transitions to `"HALF_OPEN"`, appending a `"HalfOpened"` event.
  - If state is still `"OPEN"` (cooldown not elapsed), the call is not permitted:
    raise `ValueError` with NO mutation (state, counters, clock, events unchanged).
  - Otherwise commit `clock = now`.
- `record_success(now)`:
  - From `"HALF_OPEN"`: transition to `"CLOSED"`, reset `failures` to 0,
    `opened_at` to `None`, append a `"Closed"` event.
  - From `"CLOSED"`: reset `failures` to 0.
- `record_failure(now)`:
  - From `"HALF_OPEN"`: transition back to `"OPEN"`, set `opened_at = now`,
    append an `"Opened"` event.
  - From `"CLOSED"`: increment `failures`; when it reaches `max_failures`,
    transition to `"OPEN"`, set `opened_at = now`, append an `"Opened"` event.

Only edit `src/retry.py`.
