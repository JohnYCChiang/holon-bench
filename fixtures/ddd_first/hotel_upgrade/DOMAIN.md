# Domain: Hotel Room Upgrade (bounded context)

Implement `src/hotel.py` to satisfy these rules.

## Reservation (aggregate root)
- Room classes are ranked `STANDARD < DELUXE < SUITE` with nightly rates
  `STANDARD=100, DELUXE=160, SUITE=250`.
- Created with a `room_class` (must be a known class) and a positive integer `nights`
  (`ValueError` otherwise). Optionally an `available` set of classes the property can
  offer (defaults to all classes). Starts with an empty `events` list.
- `upgrade(target)`:
  - `target` must be a known class (`ValueError`).
  - The target must rank strictly higher than the current class — same-class or
    downgrade is a domain error (`ValueError`).
  - The target must be in `available` (`ValueError`).
  - A rejected upgrade must not mutate state.
  - On success, set `room_class` to `target`, append `"Upgraded:<target>"` to `events`,
    and return the surcharge `(target_rate - current_rate) * nights`.

Only edit `src/hotel.py`.
