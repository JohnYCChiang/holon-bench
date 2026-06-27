# Domain: Seating (bounded context)

Implement `src/seating.py`. A `SeatMap` manages temporary seat holds that
expire on a logical clock, plus confirmed bookings.

## SeatMap (aggregate root)
- Created with a positive integer `seat_count`; seats are ids `1..seat_count`.
  Starts with a logical clock `now == 0`, no holds, no confirmed seats.
- A hold is *active* while `now < expiry`; at or after `expiry` it is expired
  and the seat is free again (lazy expiry — no sweep needed).
- `hold(seat, ttl)` places a hold expiring at `now + ttl`.
  - Invariant: `seat` is an integer in `1..seat_count` (`ValueError` otherwise).
  - Invariant: `ttl` is a positive integer (`ValueError` otherwise).
  - Invariant: the seat must be free — neither confirmed nor under an active
    hold (`ValueError` otherwise). A rejected command must not mutate state.
- `tick(seconds)` advances the clock by a positive integer `seconds`.
- `confirm(seat)` turns an active hold into a permanent booking.
  - Invariant: the seat must have an active (non-expired) hold (`ValueError`
    otherwise — including expired holds, no hold, or already confirmed).
  - On success the hold is consumed and the seat becomes confirmed.
- `is_free(seat)` is True when the seat is neither confirmed nor under an active
  hold at the current time.
- `available_count()` returns how many seats are free right now.

Only edit `src/seating.py`.
