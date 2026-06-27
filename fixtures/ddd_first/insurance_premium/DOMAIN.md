# Domain: Insurance Premium (bounded context)

Implement `src/insurance.py` to satisfy these rules. All money is in integer cents and
all arithmetic is integer (floor) division for determinism.

## InsurancePolicy (aggregate root)
- Created with `base_cents` (positive int, `ValueError` otherwise).
- Class constant `CLAIM_SURCHARGE = 5000`.
- `quote(age, prior_claims, loyalty_years)` computes the premium in this exact order:
  1. Validate: `18 <= age <= 120`, `prior_claims >= 0`, `loyalty_years >= 0`
     (`ValueError` otherwise).
  2. Age band multiplier (percent): `age < 25` -> 150, `age >= 60` -> 130, else 100.
     `premium = base_cents * pct // 100`.
  3. Add `prior_claims * CLAIM_SURCHARGE`.
  4. Loyalty discount: `off = min(loyalty_years, 5) * 2` percent;
     `premium = premium * (100 - off) // 100`.
  5. Floor the result at `base_cents // 2`: `premium = max(premium, base_cents // 2)`.
  - Returns the integer premium in cents.

Only edit `src/insurance.py`.
