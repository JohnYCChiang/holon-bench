//! Authoritative buff bookkeeping. `sweep` removes expired buffs and returns the
//! survivors in a deterministic order so two servers replaying the same state
//! agree regardless of how the buffs were inserted.

#[derive(Clone, Debug, PartialEq)]
pub struct Buff {
    pub id: u32,
    pub magnitude: i32,
    pub expires_at: u64,
}

/// Remove every buff whose `expires_at` is at or before `now` (a buff expiring
/// exactly on `now` is gone) and return the survivors sorted by ascending
/// `expires_at`, ties broken by ascending `id`. The result is independent of the
/// input order.
pub fn sweep(buffs: &[Buff], now: u64) -> Vec<Buff> {
    // BUG: keeps buffs that expire exactly on `now` and preserves insertion order
    // instead of the deterministic sort.
    buffs
        .iter()
        .filter(|b| b.expires_at >= now)
        .cloned()
        .collect()
}
