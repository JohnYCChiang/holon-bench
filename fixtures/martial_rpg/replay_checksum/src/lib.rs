//! Deterministic replay checksum for a martial-arts simulation.
//!
//! A replay is a list of per-entity state deltas. The authoritative checksum
//! must depend only on the *content* of the replay, not on the order the
//! network happened to deliver the events: events are folded in ascending
//! `entity_id` order (stable for equal ids). The fold itself is order-sensitive
//! so that distinct replays produce distinct checksums.

pub struct Event {
    pub entity_id: u32,
    pub delta: i64,
}

const FNV_OFFSET: u64 = 1469598103934665603;
const FNV_PRIME: u64 = 1099511628211;

/// Compute the authoritative replay checksum.
pub fn replay_checksum(events: &[Event]) -> u64 {
    // BUG: folds in network-delivery order, so two replays with the same content
    // delivered in a different order produce different checksums (replay parity
    // is broken). The authoritative order is ascending entity_id (stable).
    let mut h = FNV_OFFSET;
    for event in events {
        h ^= event.entity_id as u64;
        h = h.wrapping_mul(FNV_PRIME);
        h ^= event.delta as u64;
        h = h.wrapping_mul(FNV_PRIME);
    }
    h
}
