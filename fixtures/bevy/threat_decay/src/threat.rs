#[derive(Clone, Debug, Default, PartialEq)]
pub struct ThreatTable {
    pub entries: Vec<(u32, f32)>,
}

impl ThreatTable {
    pub fn new() -> Self {
        ThreatTable { entries: Vec::new() }
    }

    pub fn add(&mut self, id: u32, amount: f32) {
        if let Some(e) = self.entries.iter_mut().find(|e| e.0 == id) {
            e.1 += amount;
        } else {
            self.entries.push((id, amount));
        }
    }
}

/// Decay every entry's threat toward zero. Threat must never go negative.
pub fn decay(table: &mut ThreatTable, amount: f32) {
    for e in &mut table.entries {
        e.1 -= amount;
    }
}

/// The current aggro target: the entry with the highest positive threat. Ties
/// break toward the lowest id. Entries at or below zero threat are ignored.
pub fn top_target(table: &ThreatTable) -> Option<u32> {
    let mut best: Option<(u32, f32)> = None;
    for &(id, th) in &table.entries {
        match best {
            Some((_, bth)) if th > bth => best = Some((id, th)),
            None => best = Some((id, th)),
            _ => {}
        }
    }
    best.map(|(id, _)| id)
}
