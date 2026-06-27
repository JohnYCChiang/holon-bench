/// Resolve incoming damage against armor.
///
/// Rules:
/// - Non-positive raw damage deals nothing.
/// - Otherwise armor reduces damage, but a positive hit always deals at least
///   1 point of chip damage (mitigated damage is never reduced below 1).
pub fn resolve_damage(raw: i32, armor: i32) -> i32 {
    raw - armor
}

/// Apply resolved damage to a health pool, clamping at zero.
pub fn apply(hp: i32, damage: i32) -> i32 {
    hp - damage
}
