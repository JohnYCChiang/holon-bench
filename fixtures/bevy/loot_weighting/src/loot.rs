#[derive(Clone, Copy, Debug, PartialEq)]
pub struct LootEntry {
    pub id: u32,
    pub weight: u32,
}

pub fn total_weight(entries: &[LootEntry]) -> u32 {
    entries.iter().map(|e| e.weight).sum()
}

/// Pick the entry whose cumulative-weight band contains `roll`, where `roll`
/// is in `[0, total_weight)`. Each entry owns the half-open band
/// `[prev_cumulative, cumulative)`, so a zero-weight entry owns an empty band
/// and can never be selected. Returns `None` only when total weight is zero.
pub fn pick(entries: &[LootEntry], roll: u32) -> Option<u32> {
    let mut cumulative = 0u32;
    for e in entries {
        cumulative += e.weight;
        if roll <= cumulative {
            return Some(e.id);
        }
    }
    None
}
