# Domain: Meeting Rooms (bounded context)

Implement `src/meeting_room.py` to satisfy these rules.

## TimeSlot (value object)
- Immutable; equality by value. `start` and `end` are integer minutes; the range is
  half-open `[start, end)`. Constructing a slot with `start >= end` is a domain error
  (`ValueError`).
- `overlaps(other)` is True iff the two half-open ranges intersect. Back-to-back slots
  (one ends exactly when the next begins) do NOT overlap.

## Room (aggregate root)
- Created with a positive integer `capacity` (`ValueError` otherwise).
- `book(slot, attendees)`:
  - `attendees` must be a positive integer and may not exceed `capacity` (`ValueError`).
  - The slot may not overlap any existing booking (`ValueError`).
  - A rejected booking must not mutate state.
  - On success, records `(slot, attendees)`.

Only edit `src/meeting_room.py`.
