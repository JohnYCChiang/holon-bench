//! 32-bit rolling checksum. The running state is updated with a multiply-add
//! recurrence whose arithmetic must wrap modulo 2^32 — it must never panic on
//! overflow. Empty input returns 0.

/// Compute the rolling checksum of `data`.
pub fn checksum(data: &[u8]) -> u32 {
    let mut state: u32 = 0;
    for &b in data {
        state = state * 31 + b as u32; // BUG: overflows and panics in debug builds
    }
    state
}
