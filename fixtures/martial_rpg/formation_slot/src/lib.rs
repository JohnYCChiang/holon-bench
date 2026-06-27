//! Authoritative formation slot assignment. Units compete for a fixed number of
//! ordered slots. The server assigns slots deterministically by priority (higher
//! first), breaking ties by ascending id, independent of input order. Units that
//! do not fit are left unassigned (slot -1). No two assigned units may share a
//! slot.

pub struct Unit {
    pub id: u32,
    pub priority: u32,
}

/// Returns `(unit_id, slot)` pairs sorted by ascending unit id. Slots are
/// 0-based and contiguous; an unassigned unit gets slot -1.
pub fn assign(units: &[Unit], slots: usize) -> Vec<(u32, i32)> {
    // BUG: trusts input order, assigns the raw input index as the slot, and
    // ignores the slot cap (so units overflow and slots are not contiguous).
    let mut out = Vec::new();
    for (i, u) in units.iter().enumerate() {
        out.push((u.id, i as i32));
    }
    out
}
