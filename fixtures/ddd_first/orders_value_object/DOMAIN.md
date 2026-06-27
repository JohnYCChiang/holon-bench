# Domain: Ordering (bounded context)

Ubiquitous language and rules. Implement `src/orders.py` to satisfy them.

## Money (value object)
- Immutable; equality by value.
- `amount` is an integer in minor units (e.g. cents); `currency` is a string code.
- `Money.add(other)` returns a new `Money`. Adding across different currencies is
  a domain error (`ValueError`).

## Order (aggregate root)
- Created for a single `currency`.
- `add_item(name, price, quantity)` appends a line item.
  - Invariant: every line item's `price.currency` must equal the order currency
    (`ValueError` otherwise).
  - Invariant: `quantity` must be a positive integer (`ValueError` otherwise).
- `total()` returns a `Money` equal to the sum of `price.amount * quantity` across
  all line items, in the order currency. An empty order totals `Money(0, currency)`.

Only edit `src/orders.py`.
