# Domain: Ticket Refund Policy (bounded context)

Implement `src/refund.py` to satisfy these rules. Money is in integer cents and
arithmetic is integer (floor) division.

## RefundPolicy (value object / policy)
- Class constant `SERVICE_FEE = 500` (non-refundable cents).
- `refund(price_cents, days_before)`:
  - `price_cents` must be a positive integer; `days_before` must be a non-negative
    integer (`ValueError` otherwise).
  - `refundable = max(price_cents - SERVICE_FEE, 0)`.
  - Refund percentage by `days_before`: `>= 7` -> 100, `>= 3` -> 50, else 0.
  - Returns `refundable * pct // 100`.

Only edit `src/refund.py`.
