//! Deterministic seeded deck shuffle (authoritative, replay-stable).

pub struct Deck {
    pub size: usize,
}

/// Produce the deck ordering as a permutation of `0..size`, derived from `seed`.
pub fn shuffle(deck: &Deck, seed: u64) -> Vec<usize> {
    // BUG: maps each slot independently through the seed, producing collisions
    // (duplicate / missing cards), so it is not a real permutation.
    let n = deck.size.max(1);
    (0..deck.size)
        .map(|i| ((seed as usize).wrapping_add(i * i)) % n)
        .collect()
}
