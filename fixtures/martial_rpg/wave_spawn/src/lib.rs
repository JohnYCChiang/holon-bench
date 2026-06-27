//! Deterministic wave spawn budgeting.
//!
//! A wave plan must be a pure function of the spawner seed, the point budget,
//! and the per-type costs: the same inputs always yield the same spawn list, and
//! the total spent never exceeds the budget. Replays processed in a different
//! order must produce identical waves, so the plan must not depend on how many
//! waves were planned before.

pub struct WaveSpawner {
    seed: u64,
}

impl WaveSpawner {
    pub fn new(seed: u64) -> Self {
        WaveSpawner { seed }
    }

    /// Plan a wave: return the ordered indices of spawned enemy types whose total
    /// cost is `<= budget`. Only types with `0 < cost <= remaining budget` are
    /// eligible; selection among the eligible types is seeded and deterministic.
    /// The plan is a pure function of `(seed, budget, costs)`.
    pub fn plan(&mut self, budget: u32, costs: &[u32]) -> Vec<usize> {
        // BUG: spawns `budget` enemies regardless of their cost (so the total
        // cost blows past the budget) and advances the internal seed every call,
        // making the plan depend on call order (replay parity is broken).
        let mut out = Vec::new();
        if costs.is_empty() {
            return out;
        }
        for _ in 0..budget {
            self.seed = self
                .seed
                .wrapping_mul(6364136223846793005)
                .wrapping_add(1442695040888963407);
            out.push((self.seed as usize) % costs.len());
        }
        out
    }
}
