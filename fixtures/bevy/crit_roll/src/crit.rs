/// Resolve a hit's damage. The hit crits when `roll` (expected in 0..100) is
/// strictly below `chance`; a crit deals `base * crit_mult_pct / 100`, a normal
/// hit deals `base`. The comparison is half-open so `roll == chance` never crits
/// and a chance of zero can never crit.
pub fn resolve(base: i32, roll: i32, chance: i32, crit_mult_pct: i32) -> i32 {
    if is_crit(roll, chance) {
        base * crit_mult_pct / 100
    } else {
        base
    }
}

/// Whether a given roll crits at the given chance.
pub fn is_crit(roll: i32, chance: i32) -> bool {
    // BUG: uses <= so the boundary roll crits and chance 0 still crits on roll 0.
    roll <= chance
}
