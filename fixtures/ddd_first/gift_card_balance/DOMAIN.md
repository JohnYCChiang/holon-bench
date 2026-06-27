# Domain: Gift Cards (bounded context)

Implement `src/giftcard.py` to satisfy these rules.

## GiftCard (aggregate root)
- Created with a positive integer `max_balance` (`ValueError` otherwise).
- Starts with `balance == 0` and an empty `events` list.
- `load(amount)` adds value to the card.
  - Invariant: `amount` must be a positive integer (`ValueError` otherwise).
  - Invariant: `balance + amount` may never exceed `max_balance` (`ValueError`).
  - A rejected command must not mutate state.
  - On success: increase `balance` and append a `"Loaded"` event.
- `redeem(amount)` spends value.
  - Invariant: `amount` is a positive integer and `amount <= balance`
    (`ValueError` otherwise). A rejected redeem must not mutate state.
  - On success: decrease `balance` and append a `"Redeemed"` event.
- `available()` returns `max_balance - balance`.

Only edit `src/giftcard.py`.
