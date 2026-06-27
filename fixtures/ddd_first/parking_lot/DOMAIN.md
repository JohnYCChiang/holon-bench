# Domain: Parking (bounded context)

Implement `src/parking.py`. A `ParkingLot` allocates slots to vehicles.

## ParkingLot (aggregate root)
- Created with positive integers `small_slots` and `large_slots` (`ValueError`).
- Tracks free slots per type and an `events` list (starts empty).
- `park(plate, size)` allocates one slot.
  - Invariant: `size` must be `"small"` or `"large"` (`ValueError`).
  - Invariant: `plate` must be non-empty and not already parked (`ValueError`).
  - Allocation policy:
    - a `"large"` vehicle requires a free large slot; otherwise `ValueError`.
    - a `"small"` vehicle takes a free small slot if one exists, otherwise a free
      large slot; if neither exists `ValueError`.
  - A rejected command must not mutate state.
  - On success: record which slot type the vehicle occupies and append a
    `"Parked"` event.
- `leave(plate)` frees the vehicle's slot.
  - Invariant: `plate` must be currently parked (`ValueError`).
  - On success: free the occupied slot type and append a `"Departed"` event.
- `available_small()` / `available_large()` return free slot counts.
- `occupancy()` returns the number of parked vehicles.

Only edit `src/parking.py`.
