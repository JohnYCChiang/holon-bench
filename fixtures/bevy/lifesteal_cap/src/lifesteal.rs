#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Fighter {
    pub hp: i32,
    pub max_hp: i32,
}

impl Fighter {
    pub fn new(hp: i32, max_hp: i32) -> Self {
        Fighter { hp, max_hp }
    }
}

/// Heal the attacker for `ratio_pct` percent of the damage it dealt. Healing is
/// integer-floored, never applies for a non-positive hit, and the attacker's hp
/// is capped at `max_hp`.
pub fn apply_lifesteal(f: &mut Fighter, damage: i32, ratio_pct: i32) {
    // BUG: heals on any damage value (even non-positive) and never caps at max_hp.
    let heal = damage * ratio_pct / 100;
    f.hp += heal;
}
