# Domain: Taxation (bounded context)

Implement `src/tax.py`: an immutable progressive `TaxSchedule` value object and a
`TaxReturn` aggregate.

## TaxSchedule (value object)
- Immutable; equality by value.
- Field `brackets`: a tuple of `(upper_bound, rate_percent)` pairs ordered from
  lowest band to highest.
- Validation on construction (`ValueError` otherwise):
  - `brackets` is non-empty.
  - Every `rate_percent` is an integer in `0..100`.
  - Only the LAST bracket may have `upper_bound is None` (open-ended); all earlier
    bounds are positive integers.
  - Bounds are strictly ascending.
- `tax_for(income)` computes progressive tax:
  - Invariant: `income` is a non-negative integer (`ValueError`).
  - Income is taxed band by band: the portion of income falling in each band is
    taxed at that band's rate; per-band tax is floored (`portion * rate // 100`).
  - Returns the total tax.

## TaxReturn (aggregate root)
- Created with a `TaxSchedule`; starts with `income == 0`, `filed == False`, an
  empty `events` list.
- `add_income(amount)`:
  - Invariant: `amount` is a positive integer (`ValueError`).
  - Invariant: the return must not already be filed (`ValueError`).
  - A rejected command must not mutate state.
  - On success: increase `income`, append an `"IncomeRecorded"` event.
- `file()`:
  - Invariant: the return must not already be filed (`ValueError`).
  - On success: set `filed = True`, append a `"Filed"` event, return the computed
    liability for the recorded income.
- `current_liability()` returns `schedule.tax_for(income)`.

Only edit `src/tax.py`.
