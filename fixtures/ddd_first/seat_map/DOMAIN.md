# Domain: Seat-Map Assignment (bounded context)

Implement `src/seatmap.py` to satisfy these rules. The aggregate guards seat
assignment invariants and records domain events. Group bookings are ATOMIC.

## SeatMap (aggregate root)
- Created with positive integers `rows` and `cols` (`ValueError` otherwise). Seats are
  `(row, col)` 1-indexed. Tracks `assignments` (seat -> passenger),
  `passenger_seat` (passenger -> seat), and an `events` list.
- `assign(passenger, seat)`:
  - The seat must be within range (`ValueError`).
  - The seat must be free and the passenger must not already be seated (`ValueError`).
  - On success record the assignment and append `"Assigned:<passenger>:<row>-<col>"`.
- `release(passenger)`:
  - The passenger must be seated (`ValueError`). Frees their seat and appends
    `"Released:<passenger>"`.
- `assign_group(passengers, row)`:
  - `passengers` must be a non-empty list with no duplicates, `row` must be in range,
    and no listed passenger may already be seated (`ValueError` otherwise).
  - Find the earliest (lowest column) run of `len(passengers)` consecutive FREE seats
    in `row` and seat the passengers left-to-right. If no such run exists, raise
    `ValueError`.
  - The command is atomic: on any rejection NOTHING is mutated and no event is recorded.
  - On success append `"GroupAssigned:<row>:<start_col>:<count>"`.

Only edit `src/seatmap.py`.
