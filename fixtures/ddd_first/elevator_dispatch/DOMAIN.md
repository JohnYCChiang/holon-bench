# Domain: Elevator Dispatch (bounded context)

Implement `src/elevator.py`. An `Elevator` is an authoritative deterministic
state machine that services floor requests with a LOOK policy and emits a door
event on each arrival. Client input is never trusted to drive state directly.

## Elevator (aggregate root)
- Created with an integer `floors >= 2`. Floors are numbered `1..floors`.
  Starts at floor 1, `direction == "IDLE"`, no pending requests, empty `events`.
- `request(floor)` registers a stop.
  - Invariant: `floor` is an integer in `1..floors` (`ValueError` otherwise); a
    rejected request must not mutate state.
  - Requesting the current floor is a no-op (no stop is queued, no event).
  - Duplicate requests are idempotent.
- `step()` advances exactly one floor under the LOOK policy:
  - With no pending requests: set `direction = "IDLE"` and do not move.
  - While moving `"UP"`, keep going up if any request is above; otherwise if any
    request is below, switch to `"DOWN"`. Symmetrically for `"DOWN"`.
  - From `"IDLE"` with requests, choose the direction of the nearest request;
    ties (equal distance up and down) resolve `"UP"`.
  - Move one floor in the chosen direction. On arriving at a requested floor,
    remove that request and append a `"DoorOpened"` event.
- `run()` repeatedly `step()`s until no requests remain, returning the list of
  floors where doors opened, in service order.
- `pending()` returns the sorted list of pending request floors.

Only edit `src/elevator.py`.
