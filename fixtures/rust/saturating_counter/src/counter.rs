/// Apply a sequence of deltas to a u8 counter, saturating at the bounds 0..=255.
pub fn apply(start: u8, deltas: &[i32]) -> u8 {
    let mut current = start;
    for &d in deltas {
        // BROKEN: cast wraps around instead of saturating.
        current = (current as i32 + d) as u8;
    }
    current
}
