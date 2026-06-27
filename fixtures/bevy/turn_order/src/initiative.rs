#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Unit {
    pub id: u32,
    pub speed: u32,
}

/// Compute the turn order for a round of combat.
///
/// Faster units act first. When two units share the same speed, the tie is
/// broken deterministically by ascending id so the order never depends on the
/// input arrangement.
pub fn turn_order(units: &[Unit]) -> Vec<u32> {
    let mut sorted = units.to_vec();
    sorted.sort_by(|a, b| b.speed.cmp(&a.speed));
    sorted.iter().map(|u| u.id).collect()
}
