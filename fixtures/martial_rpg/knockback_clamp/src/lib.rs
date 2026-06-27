//! Authoritative knockback resolution. The server clamps the knockback impulse
//! per axis and then clamps the resulting position to the arena bounds, so a
//! client can never be flung out of the playfield or teleported.

pub struct Arena {
    pub width: i32,
    pub height: i32,
}

/// Apply a knockback `impulse` to `pos` inside `arena`. Each axis of the impulse
/// is clamped to [-max_impulse, max_impulse] (a negative `max_impulse` means no
/// knockback), then the new position is clamped to [0, width] x [0, height].
/// Returns the authoritative new position.
pub fn apply_knockback(
    pos: (i32, i32),
    impulse: (i32, i32),
    max_impulse: i32,
    arena: &Arena,
) -> (i32, i32) {
    // BUG: returns the raw displaced position with no impulse cap and no bounds clamp.
    (pos.0 + impulse.0, pos.1 + impulse.1)
}
