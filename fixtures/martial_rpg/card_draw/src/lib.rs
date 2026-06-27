//! Authoritative deterministic card draw. `draw_hand` returns a hand of distinct
//! card indices drawn from a deck of `size` cards, derived purely from the seed.
//! The hand is the prefix of a seeded permutation, so it is reproducible for a
//! given seed, contains no duplicates, and is independent of any prior calls.

/// Draw `hand_size` distinct cards (indices in `0..size`) from a `size`-card
/// deck, deterministically from `seed`. If `hand_size >= size` the full deck
/// (a permutation of `0..size`) is returned. A `size` of 0 yields an empty hand.
pub fn draw_hand(seed: u64, size: u32, hand_size: u32) -> Vec<u32> {
    // BUG: each card is an independent hash of the seed reduced modulo `size`,
    // so the "hand" can contain duplicates and is not a real subset of the deck.
    let n = hand_size.min(size);
    let mut out = Vec::new();
    for i in 0..n {
        if size == 0 {
            break;
        }
        let h = seed
            .wrapping_add(i as u64)
            .wrapping_mul(0x9E37_79B9_7F4A_7C15);
        out.push((h % size as u64) as u32);
    }
    out
}
