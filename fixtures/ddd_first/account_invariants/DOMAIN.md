# Domain: Account (bounded context)

Implement `src/account.py` to satisfy these rules.

## BankAccount (aggregate root)
- Created with a positive `daily_limit`. Starts at `balance = 0` and
  `withdrawn_today = 0`.
- `deposit(amount)`:
  - Invariant: `amount` must be a positive integer (`ValueError` otherwise).
  - Increases `balance`.
- `withdraw(amount)`:
  - Invariant: `amount` must be a positive integer (`ValueError` otherwise).
  - Invariant: balance may never go negative — withdrawing more than `balance`
    is a domain error (`ValueError`).
  - Invariant: cumulative withdrawals in the session may not exceed `daily_limit`
    — a withdrawal that would cross the limit is a domain error (`ValueError`).
  - On success, decreases `balance` and increases `withdrawn_today`.

A rejected command must not mutate any state (no partial application).

Only edit `src/account.py`.
