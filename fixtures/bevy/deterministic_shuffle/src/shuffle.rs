fn next_state(state: u64) -> u64 {
    state
        .wrapping_mul(6364136223846793005)
        .wrapping_add(1442695040888963407)
}

/// Deterministically shuffle `items` in place using a Fisher-Yates pass driven
/// by a 64-bit LCG seeded with `seed`. For each index `i` from the end down to
/// 1, a partner index `j` is drawn uniformly from the inclusive range `0..=i`
/// and the two are swapped. The result is a permutation of the input and is
/// identical for a given seed.
pub fn shuffle(items: &mut [u32], seed: u64) {
    let mut state = seed;
    let n = items.len();
    for i in (1..n).rev() {
        state = next_state(state);
        // BUG: draws j from 0..i instead of the inclusive 0..=i, biasing the
        // shuffle (an element can never keep its own slot).
        let j = (state % (i as u64)) as usize;
        items.swap(i, j);
    }
}
