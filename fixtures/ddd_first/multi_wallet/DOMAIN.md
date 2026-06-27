# Domain: Multi-Balance Wallet (bounded context)

Implement `src/wallet.py` to satisfy these rules. A wallet holds independent balances
per currency.

## Wallet (aggregate root)
- Starts with no balances. `balance(currency)` returns the integer balance (0 if the
  currency was never seen).
- `deposit(currency, amount)`: `amount` must be a positive integer (`ValueError`);
  increases that currency's balance.
- `withdraw(currency, amount)`: `amount` must be a positive integer (`ValueError`);
  the currency's balance must be at least `amount` (`ValueError` otherwise, treating an
  unseen currency as 0). A rejected withdrawal must not mutate state.
- `transfer(other, currency, amount)`: atomically withdraw from `self` and deposit into
  the `other` wallet. If the withdrawal is rejected, neither wallet is mutated.
- Currencies are independent: operating on one currency never affects another.

Only edit `src/wallet.py`.
