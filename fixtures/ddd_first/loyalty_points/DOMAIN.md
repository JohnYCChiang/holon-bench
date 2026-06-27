# Domain: Loyalty (bounded context)

Implement `src/loyalty.py`. A `LoyaltyAccount` accrues and redeems points and
emits domain events. Tier is based on *lifetime* earned points and never
downgrades.

## LoyaltyAccount (aggregate root)
- Starts with `balance == 0`, `lifetime_earned == 0`, an empty `events` list.
- `GOLD_THRESHOLD == 1000` lifetime points.
- `earn(amount_cents)` accrues 1 point per whole dollar (`amount_cents // 100`).
  - Invariant: `amount_cents` is a positive integer (`ValueError` otherwise).
  - If the purchase yields 0 points (`amount_cents < 100`) it is a valid command
    that changes nothing and records no event.
  - On a positive accrual: increase `balance` and `lifetime_earned`, append a
    `"PointsEarned"` event. If `lifetime_earned` reaches `GOLD_THRESHOLD`,
    append a `"TierUpgraded"` event exactly once (never again).
- `redeem(points)` spends points.
  - Invariant: `points` is a positive integer and `points <= balance`
    (`ValueError` otherwise). A rejected redeem must not mutate state.
  - On success: decrease `balance` and append a `"PointsRedeemed"` event.
- `tier()` returns `"GOLD"` when `lifetime_earned >= GOLD_THRESHOLD`, else
  `"STANDARD"`.

Only edit `src/loyalty.py`.
