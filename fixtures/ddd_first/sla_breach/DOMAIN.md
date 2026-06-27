# Domain: SLA Monitoring (bounded context)

Implement `src/sla.py`. An `SLAMonitor` watches a metric against a threshold and
latches a breach after a run of consecutive over-threshold readings, emitting a
domain event exactly once per breach episode.

## SLAMonitor (aggregate root)
- Created with a non-negative integer `threshold` and a positive integer
  `tolerance` (the number of consecutive over-threshold readings that triggers a
  breach). Starts with `consecutive == 0`, not breached, empty `events`.
- `record(value)` ingests one reading.
  - Invariant: `value` is a non-negative integer (`ValueError` otherwise); a
    rejected reading must not mutate state.
  - If `value > threshold`: increment the consecutive counter. When the counter
    first reaches `tolerance`, latch the breach and append a `"SLABreached"`
    event — exactly once; subsequent over-threshold readings do not re-emit while
    still breached.
  - If `value <= threshold`: the reading is healthy — reset the consecutive
    counter to 0 and clear the latched breach (a new breach may latch later).
- `is_breached()` returns the current latched breach state.
- `breach_count()` returns how many `"SLABreached"` events have been emitted.

Only edit `src/sla.py`.
