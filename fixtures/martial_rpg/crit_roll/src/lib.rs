//! Authoritative crit resolution. `is_crit` must be a pure function of
//! (seed, attacker_id, tick, crit_chance_pct) so a replay produces the same crits
//! regardless of how many rolls were processed before, or in what order.

pub struct CritRoller {
    pub seed: u64,
    state: u64,
}

impl CritRoller {
    pub fn new(seed: u64) -> Self {
        CritRoller { seed, state: seed }
    }

    /// Return true if the attack crits. `crit_chance_pct` is clamped to [0, 100]:
    /// 0 never crits, 100 always crits. The decision must depend only on
    /// (seed, attacker_id, tick, crit_chance_pct), never on call order.
    pub fn is_crit(&mut self, attacker_id: u64, tick: u64, crit_chance_pct: u32) -> bool {
        // BUG: advances a mutable internal state, so the outcome depends on how
        // many rolls came before -> replays delivered in a different order diverge.
        self.state = self
            .state
            .wrapping_mul(6364136223846793005)
            .wrapping_add(attacker_id ^ tick);
        let roll = (self.state % 100) as u32;
        roll < crit_chance_pct
    }
}
