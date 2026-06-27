# Domain: Inventory (bounded context)

Implement `src/inventory.py` to satisfy these rules. This aggregate records
domain events and a reorder policy reacts to them.

## Inventory (aggregate root, one SKU)
- Created with `available` (>= 0) and `reorder_to` (> 0). Starts with an empty
  `events` list.
- `reserve(qty)`:
  - Invariant: `qty` must be a positive integer (`ValueError` otherwise).
  - Invariant: stock may never go negative — reserving more than `available` is a
    domain error (`ValueError`), and a rejected reservation must not mutate state.
  - On success, decreases `available`.
  - When `available` reaches exactly 0, append a `"StockDepleted"` domain event —
    exactly once per depletion (not on every reserve, and not again until restocked).
- `apply_reorder_policy()`:
  - If a depletion is pending (a `"StockDepleted"` not yet handled), restock
    `available` to `reorder_to`, append a `"Reordered"` event, and clear the
    pending depletion.
  - Idempotent: calling it again with nothing pending does nothing (no duplicate
    `"Reordered"`).

Only edit `src/inventory.py`.
