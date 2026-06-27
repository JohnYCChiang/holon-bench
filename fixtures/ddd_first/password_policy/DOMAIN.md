# Domain: Credentials (bounded context)

Implement `src/password.py`: an immutable `PasswordPolicy` value object and a
`Credential` aggregate that enforces it.

## PasswordPolicy (value object)
- Immutable; equality by value.
- Fields: `min_length` (positive integer, `ValueError` otherwise),
  `require_digit` (bool), `require_symbol` (bool).
- Symbols are exactly the characters in `"!@#$%^&*"`.
- `violations(password)` returns a `tuple` of rule codes that FAIL, in this
  fixed order, including only codes for active rules:
  - `"too_short"` when `len(password) < min_length`.
  - `"missing_digit"` when `require_digit` and the password has no digit.
  - `"missing_symbol"` when `require_symbol` and the password has no symbol.
- `is_valid(password)` returns `True` iff `violations(password)` is empty.

## Credential (aggregate root)
- Created with a `PasswordPolicy`; starts with `password is None`, an empty
  `history` list, and an empty `events` list.
- `set_password(pw)`:
  - Invariant: `pw` must satisfy the policy (`ValueError` otherwise).
  - Invariant: `pw` must not equal any password in `history` (`ValueError`).
  - A rejected command must not mutate state.
  - On success: set `password`, append `pw` to `history`, append a
    `"PasswordSet"` event.

Only edit `src/password.py`.
