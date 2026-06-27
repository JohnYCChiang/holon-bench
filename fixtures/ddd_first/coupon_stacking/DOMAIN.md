# Domain: Coupons (bounded context)

Implement `src/coupons.py`. A `Coupon` value object describes a discount; a
`Checkout` aggregate applies coupons under stacking rules and prices the cart
deterministically.

## Coupon (value object)
- Immutable; equality by value. Fields: `code` (non-empty str), `kind`
  (`"PERCENT"` or `"FIXED"`), `value` (int), `stackable` (bool).
  - Invariant: `kind` must be `"PERCENT"` or `"FIXED"` (`ValueError` otherwise).
  - Invariant: a `"PERCENT"` coupon's `value` is an integer in `1..100`.
  - Invariant: a `"FIXED"` coupon's `value` is a positive integer (cents).
  - Invariant: `code` is a non-empty string.

## Checkout (aggregate root)
- Constructed with a positive integer `subtotal` (cents); starts with no coupons.
- `apply(coupon)` adds a coupon under the stacking policy.
  - Invariant: the same `code` may not be applied twice (`ValueError`).
  - Invariant: a non-stackable coupon may only be applied when no coupon is
    present, and once a non-stackable coupon is present no further coupon may be
    applied (a non-stackable coupon must be the only one). Violations raise
    `ValueError` and must not mutate state.
- `total()` prices the cart by applying coupons in insertion order to a running
  total: `"PERCENT"` subtracts `running * value // 100` (floored), `"FIXED"`
  subtracts `min(value, running)`. The running total never drops below 0.
- `discount()` returns `subtotal - total()`.

Only edit `src/coupons.py`.
