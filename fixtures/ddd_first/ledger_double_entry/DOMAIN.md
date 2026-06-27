# Domain: Ledger (bounded context)

Implement `src/ledger.py` to satisfy these rules. This aggregate enforces the
double-entry invariant: every posting must balance to zero.

## Ledger (aggregate root)
- Starts with no account balances.
- `post(legs)` records a balanced transaction. `legs` is a sequence of
  `(account, amount)` pairs where `amount` is a non-zero integer (positive =
  debit, negative = credit).
  - Invariant: a transaction must have at least two legs (`ValueError` otherwise).
  - Invariant: every amount must be a non-zero integer (`ValueError` otherwise).
  - Invariant: the legs must sum to exactly 0 — an unbalanced transaction is a
    domain error (`ValueError`). A rejected posting must not mutate any balance.
  - On success, each leg's `amount` is added to that account's balance.
- `balance(account)` returns the account balance (0 for an unknown account).
- `is_balanced()` returns True when all account balances sum to 0 (always true
  after any sequence of accepted postings).

Only edit `src/ledger.py`.
