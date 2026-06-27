# Domain: Wallets (bounded context)

Implement `src/wallet.py` to satisfy these rules. A `Bank` manages many wallets
and two-phase transfers via holds. Money is conserved: the total of all wallet
balances never changes except by capturing a hold (which moves it between
wallets).

## Bank (aggregate root over wallets and holds)
- Starts with no wallets and no holds, an empty `events` list.
- `open(wallet_id, initial=0)` creates a wallet.
  - Invariant: `wallet_id` must be new (`ValueError` if it already exists).
  - Invariant: `initial` must be a non-negative integer (`ValueError` otherwise).
- `available(wallet_id)` returns `balance - held` for the wallet.
- `place_hold(wallet_id, amount)` reserves funds and returns a hold id.
  - Invariant: the wallet must exist; `amount` must be a positive integer.
  - Invariant: `available(wallet_id)` must be >= `amount` (`ValueError` otherwise).
  - On success, increases the wallet's held amount, records a `"HoldPlaced"`
    event, and returns a unique hold id. A rejected command must not mutate state.
- `capture(hold_id, to_wallet_id)` settles a hold, moving its amount to another
  wallet.
  - Invariant: the hold must exist and be active; `to_wallet_id` must exist
    (`ValueError` otherwise).
  - On success: the source wallet's balance and held both drop by the amount, the
    destination balance rises by the amount, the hold becomes inactive, and a
    `"HoldCaptured"` event is recorded. Capturing a non-active hold is rejected.
- `release(hold_id)` cancels an active hold, returning the reserved funds.
  - Invariant: the hold must exist and be active (`ValueError` otherwise).
  - On success: the source wallet's held drops by the amount, the hold becomes
    inactive, and a `"HoldReleased"` event is recorded.
- `total_balance()` returns the sum of all wallet balances.

Only edit `src/wallet.py`.
