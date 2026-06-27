# Domain: Scheduling (bounded context)

Implement `src/booking.py` to satisfy these rules.

## Interval (value object)
- Immutable; equality by value. Represents a half-open range `[start, end)` of
  integer time slots.
- `start` and `end` must be integers with `start < end`; otherwise constructing
  the Interval is a domain error (`ValueError`).
- `overlaps(other)` is True when the two ranges share any slot. Half-open ranges
  that merely touch at an endpoint (e.g. `[10, 12)` and `[12, 14)`) do NOT
  overlap.

## Calendar (aggregate root, one resource)
- Starts with no reservations.
- `book(start, end)` reserves the interval `[start, end)`.
  - Invariant: the interval must be valid (`start < end`, integers) — `ValueError`
    otherwise.
  - Invariant: the new interval must not overlap any existing reservation
    (`ValueError` otherwise). A rejected booking must not mutate state.
  - On success, records the reservation.
- `is_free(start, end)` returns True when `[start, end)` overlaps no reservation.

Only edit `src/booking.py`.
