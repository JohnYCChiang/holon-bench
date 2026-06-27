//! Authoritative status-effect stacking.
//!
//! Duplicate effect ids stack by summing their magnitudes, but each id's total
//! is clamped to `[-cap, cap]`. The merged result must be deterministic: exactly
//! one entry per id, sorted by ascending id, independent of the order the
//! stacks were submitted over the network.

pub struct Stack {
    pub id: u32,
    pub magnitude: i32,
}

/// Merge duplicate effect ids: magnitudes of the same id sum, the per-id total
/// is clamped to `[-cap, cap]`, and the output is one entry per id sorted by id.
pub fn merge_stacks(stacks: &[Stack], cap: i32) -> Vec<Stack> {
    // BUG: keeps first-seen insertion order (not sorted by id) so two equivalent
    // replays submitted in different orders disagree, and the per-id total is
    // never clamped to `cap`.
    let mut out: Vec<Stack> = Vec::new();
    for s in stacks {
        if let Some(existing) = out.iter_mut().find(|e| e.id == s.id) {
            existing.magnitude += s.magnitude;
        } else {
            out.push(Stack {
                id: s.id,
                magnitude: s.magnitude,
            });
        }
    }
    out
}
