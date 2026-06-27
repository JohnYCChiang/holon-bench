//! Authoritative energy-shield absorption. Incoming damage is absorbed by the
//! energy shield first; only the overflow spills onto health. Both pools floor
//! at 0 and negative damage never heals.

pub struct Defense {
    pub shield: u32,
    pub hp: u32,
}

/// Apply `damage` to `defense`, shield first then health.
///
/// Negative damage is treated as 0 (no healing). The shield absorbs as much as
/// it can; the remainder reduces hp. Both values saturate at 0. Returns the
/// authoritative `(new_shield, new_hp)`.
pub fn absorb(defense: &Defense, damage: i64) -> (u32, u32) {
    // BUG: applies damage straight to hp, ignoring the shield, and underflows.
    let dmg = damage as u32;
    (defense.shield, defense.hp - dmg)
}
