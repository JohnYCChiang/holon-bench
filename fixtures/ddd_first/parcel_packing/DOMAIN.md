# Domain: Packing (bounded context)

Implement `src/box.py` to satisfy these rules.

## ShippingBox (aggregate root)
- Created with a positive `max_weight` and a positive `max_items` capacity.
- Starts empty.
- `pack(weight)` adds one item of the given `weight`.
  - Invariant: `weight` must be a positive integer (`ValueError` otherwise).
  - Invariant: total packed weight may never exceed `max_weight` (`ValueError`).
  - Invariant: the number of items may never exceed `max_items` (`ValueError`).
  - A rejected command must not mutate state (weight and count unchanged).
  - On success, records the item.
- `total_weight()` returns the sum of packed item weights (0 when empty).
- `count()` returns the number of packed items.
- `remaining_weight()` returns `max_weight - total_weight()`.

Only edit `src/box.py`.
