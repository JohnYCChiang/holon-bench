# Domain: Pricing (bounded context)

Implement `src/cart.py` to satisfy these rules.

## Discount (value object)
- Immutable; equality by value.
- `percent` is an integer in the inclusive range 0..100. Constructing a Discount
  with a percent outside that range is a domain error (`ValueError`).
- `apply_to(amount)` returns `amount` reduced by `percent`, rounded DOWN to a
  whole unit: `amount - (amount * percent) // 100`.

## Cart (aggregate root)
- Created for a single `currency`. Starts empty with no discount.
- `add_item(sku, unit_price, quantity)` appends a line item.
  - Invariant: `unit_price` must be a positive integer (minor units); `quantity`
    must be a positive integer (`ValueError` otherwise).
  - A rejected command must not mutate state.
- `apply_discount(discount)` attaches a `Discount` to the cart.
  - Invariant: a cart carries at most one discount; applying a second is a domain
    error (`ValueError`) and must not replace the existing one.
- `subtotal()` returns the sum of `unit_price * quantity` across all line items.
  An empty cart has subtotal `0`.
- `total()` returns the subtotal with the discount applied (or the subtotal when
  no discount is attached).

Only edit `src/cart.py`.
