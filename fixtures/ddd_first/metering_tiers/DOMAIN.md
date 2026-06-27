# Domain: Metering (bounded context)

Implement `src/metering.py`. A `TieredPlan` value object prices usage across
ascending tiers; a `MeteredSubscription` aggregate accumulates usage, prices it,
and bills cycles as immutable invoices.

## TieredPlan (value object)
- Immutable; equality by value. Constructed with `tiers`: a sequence of
  `(limit, rate)` pairs where `rate` is non-negative cents per unit and `limit`
  is the cumulative upper bound for that tier.
  - Invariant: at least one tier; `rate` is a non-negative integer.
  - Invariant: every `limit` except the last is a positive integer and limits
    are strictly ascending; the last tier's `limit` may be `None` meaning
    open-ended. A finite-limit final tier caps usage there (`ValueError` is not
    required for over-cap usage — see `cost`).
- `cost(units)` returns the total cents for `units` usage, charging each unit at
  the rate of the tier whose cumulative band it falls in.
  - Invariant: `units` is a non-negative integer (`ValueError` otherwise).
  - Units beyond a finite final tier's limit are not charged (capped band).

## MeteredSubscription (aggregate root)
- Constructed with a `TieredPlan`; starts with `usage == 0`, empty `invoices`
  and `events` lists.
- `record(units)` adds usage. `units` is a positive integer (`ValueError`
  otherwise); a rejected command must not mutate state.
- `current_charge()` returns `plan.cost(usage)` for the open cycle.
- `close_cycle()` finalizes the cycle: appends the current charge to `invoices`,
  appends a `"CycleInvoiced"` event, resets `usage` to 0, and returns the charge.
- `total_billed()` returns the sum of all invoices.

Only edit `src/metering.py`.
