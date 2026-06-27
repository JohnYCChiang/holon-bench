# Domain: Traffic Light Controller (bounded context)

Implement `src/traffic.py` to satisfy these rules. The controller is an authoritative
phase state machine that records domain events.

## TrafficLight (aggregate root)
- Phases cycle deterministically: `GREEN -> YELLOW -> RED -> GREEN`.
- Created with a starting phase (default `"GREEN"`); an unknown phase is a domain error
  (`ValueError`). Starts with an empty `events` list and no pending walk request.
- `advance()` moves to the next phase and appends the new phase name to `events`.
  - If a pedestrian walk request is pending and the new phase is `RED`, also append
    `"WalkGranted"` exactly once and clear the pending request.
- `request_walk()` marks a walk request pending (granted the next time the light
  reaches `RED`). A walk is never granted at `GREEN` or `YELLOW`.

Only edit `src/traffic.py`.
