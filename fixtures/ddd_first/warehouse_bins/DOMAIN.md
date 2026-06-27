# Domain: Warehouse (bounded context)

Implement `src/warehouse.py`. A `Warehouse` holds stock in capacity-bounded
bins. Receiving adds external stock; transfers move stock between bins and
conserve the total. Transfers are atomic — a rejected transfer leaves both bins
untouched.

## Warehouse (aggregate root over bins)
- Starts with no bins and an empty `events` list.
- `add_bin(bin_id, capacity)` registers a new bin starting at quantity 0.
  - Invariant: `bin_id` must be new (`ValueError` otherwise).
  - Invariant: `capacity` is a positive integer (`ValueError` otherwise).
- `receive(bin_id, qty)` adds externally-sourced stock to a bin.
  - Invariant: the bin must exist; `qty` is a positive integer.
  - Invariant: resulting quantity may not exceed the bin capacity (`ValueError`).
  - On success records a `"StockReceived"` event.
- `transfer(src, dst, qty)` moves stock between two distinct bins.
  - Invariant: both bins exist and `src != dst`; `qty` is a positive integer.
  - Invariant: `src` must hold at least `qty`.
  - Invariant: `dst` must have room (`quantity(dst) + qty <= capacity(dst)`).
  - Atomic: if any invariant fails the command is rejected and neither bin
    changes. On success records a `"StockTransferred"` event; the total stock is
    unchanged.
- `quantity(bin_id)` returns a bin's current quantity (bin must exist).
- `total_stock()` returns the sum of all bin quantities.

Only edit `src/warehouse.py`.
