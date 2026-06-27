//! Authoritative experience / level-up curve.

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Progress {
    pub level: u32,
    pub xp: u32,
}

/// Award `gained` xp, leveling up while the accumulated xp meets the per-level
/// threshold, carrying the remainder. Levels never exceed `max_level`.
pub fn award(mut p: Progress, gained: u32, _max_level: u32) -> Progress {
    // BUG: a single flat-threshold level-up, no remainder carry, ignores the
    // per-level curve and the max-level cap.
    p.xp += gained;
    if p.xp >= 100 {
        p.level += 1;
    }
    p
}
