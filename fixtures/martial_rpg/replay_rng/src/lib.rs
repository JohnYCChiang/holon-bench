//! Deterministic, replayable combat RNG.
//!
//! A roll for a given `(entity_id, tick)` must be a pure function of the seed
//! and those coordinates, so a replay processed in a different order reproduces
//! identical rolls (replay parity). Distinct coordinates must produce
//! well-mixed, distinct values.

pub struct ReplayRng {
    seed: u64,
}

impl ReplayRng {
    pub fn new(seed: u64) -> Self {
        ReplayRng { seed }
    }

    /// Deterministic roll for `(entity_id, tick)` under this seed.
    pub fn roll_for(&mut self, entity_id: u32, tick: u64) -> u64 {
        // BUG: threads a running internal state advanced on every call, so the
        // value depends on how many rolls came before -> the same replay
        // processed in a different order diverges (replay parity is broken).
        self.seed = self
            .seed
            .wrapping_mul(6364136223846793005)
            .wrapping_add(1442695040888963407);
        self.seed ^ (entity_id as u64) ^ tick
    }
}
