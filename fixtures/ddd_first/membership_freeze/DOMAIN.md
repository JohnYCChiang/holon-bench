# Domain: Gym Membership Freeze (bounded context)

Implement `src/membership.py` to satisfy these rules.

## Membership (aggregate root)
- Class constant `MAX_FREEZE = 3` (months allowed to be frozen per year).
- Starts `ACTIVE` with `frozen_used = 0` and an empty `events` list.
- `freeze(months)`:
  - `months` must be a positive integer (`ValueError`).
  - Only allowed while `ACTIVE` — freezing while already frozen is a domain error
    (`ValueError`).
  - `frozen_used + months` may not exceed `MAX_FREEZE` (`ValueError`).
  - A rejected command must not mutate state.
  - On success set state to `FROZEN`, add `months` to `frozen_used`, append
    `"Frozen:<months>"`.
- `unfreeze()`:
  - Only allowed while `FROZEN` (`ValueError`).
  - On success set state to `ACTIVE`, append `"Unfrozen"`.

Only edit `src/membership.py`.
