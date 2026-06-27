# Domain: Vending Machine Change (bounded context)

Implement `src/vending.py` to satisfy these rules.

## VendingMachine (aggregate root)
- Created with an `inventory` dict mapping coin denomination (positive int) to a
  non-negative count.
- `dispense_change(amount)` returns a dict mapping denomination -> count dispensed,
  computed by a deterministic greedy from the largest denomination down: for each
  denomination take `min(remaining // denom, available)` coins.
  - `amount` must be a non-negative integer (`ValueError` otherwise).
  - `amount == 0` returns `{}`.
  - If exact change cannot be made from the available inventory, raise `ValueError`
    and DO NOT mutate the inventory (compute the full plan before applying it).
  - On success, decrement the inventory by the dispensed coins and return the plan
    (denominations with a zero count are omitted).

Only edit `src/vending.py`.
