//! Authoritative lifesteal healing. An attacker heals for a percentage of the
//! damage it dealt, but the heal is bounded: the percentage is clamped, only
//! positive damage heals, and the attacker's hp never exceeds max_hp.

pub struct Combatant {
    pub hp: u32,
    pub max_hp: u32,
}

/// Heal `attacker` for `lifesteal_pct` percent of `damage_dealt`.
///
/// The percentage is clamped to [0, 100], only positive damage heals (negative
/// damage grants nothing), the heal uses integer math (floor), and the new hp
/// is capped at `max_hp`. Returns the authoritative new hp.
pub fn lifesteal(attacker: &Combatant, damage_dealt: i64, lifesteal_pct: i64) -> u32 {
    // BUG: does not clamp the percentage, heals on negative damage, and lets hp
    // grow past max_hp (and can overflow).
    let heal = (damage_dealt * lifesteal_pct / 100) as u32;
    attacker.hp + heal
}
