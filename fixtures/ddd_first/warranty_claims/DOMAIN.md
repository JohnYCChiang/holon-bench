# Domain: Warranty (bounded context)

Implement `src/warranty.py`. A `Warranty` approves claims within a coverage
window, up to a claim limit, on a monotonic logical day clock.

## Warranty (aggregate root)
- Created with:
  - `purchase_day`: a non-negative integer.
  - `term_days`: a positive integer coverage length.
  - `max_claims`: a positive integer claim limit.
  - (`ValueError` if any is out of range.)
- Tracks approved `claims` (a list of `(day, amount)`) and an `events` list,
  both starting empty.
- `file_claim(day, amount)`:
  - Invariant: `amount` is a positive integer (`ValueError`).
  - Invariant: `day` is an integer with `day >= purchase_day` (`ValueError`):
    a claim cannot predate purchase.
  - Invariant: `day <= purchase_day + term_days` (inclusive) or the warranty has
    expired (`ValueError`).
  - Invariant: claims must be filed in non-decreasing `day` order; a `day` earlier
    than the last approved claim is rejected (`ValueError`).
  - Invariant: the number of approved claims must be `< max_claims` (`ValueError`).
  - A rejected command must not mutate state.
  - On success: append `(day, amount)` to `claims` and append a `"ClaimApproved"`
    event.
- `claims_used()` returns the number of approved claims.
- `is_active(day)` returns `purchase_day <= day <= purchase_day + term_days`.
- `total_claimed()` returns the sum of approved claim amounts.

Only edit `src/warranty.py`.
