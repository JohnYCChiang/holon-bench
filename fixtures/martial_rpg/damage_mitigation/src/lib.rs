//! Authoritative damage mitigation pipeline.
//!
//! Incoming raw damage is reduced first by flat `armor`, then by a percentage
//! `resist_pct` applied to whatever survives the armor step. The pipeline order
//! is fixed and the final result is floored at 0. `resist_pct` is clamped to
//! `[0, 100]`.

pub struct Mitigation {
    pub armor: i32,
    pub resist_pct: i32,
}

/// Apply armor (flat) then resist (percentage) in that fixed order, flooring at 0.
pub fn mitigate(raw: i32, m: Mitigation) -> i32 {
    // BUG: applies the resist percentage before armor and never floors the
    // result, so heavy armor drives the value negative and the pipeline order
    // is wrong.
    let after_resist = raw - raw * m.resist_pct / 100;
    after_resist - m.armor
}
