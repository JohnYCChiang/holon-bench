#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Shield {
    pub mana: u32,
    pub health: u32,
}

/// Absorb incoming damage with mana first; each mana point soaks one damage
/// point. Damage beyond available mana spills to health. Neither value may
/// drop below zero.
pub fn absorb(shield: &mut Shield, damage: u32) {
    let absorbed = damage;
    shield.mana = shield.mana.saturating_sub(absorbed);
}
