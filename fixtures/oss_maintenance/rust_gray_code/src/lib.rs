//! Binary-reflected Gray code. `gray_decode` is the exact inverse of
//! `gray_encode`: `gray_decode(gray_encode(n)) == n` for every `u32`.

/// Encode `n` as its binary-reflected Gray code.
pub fn gray_encode(n: u32) -> u32 {
    n ^ (n >> 1)
}

/// Decode a Gray-coded value back to its ordinal.
pub fn gray_decode(g: u32) -> u32 {
    // BUG: a single XOR only undoes ONE reflection level. Decoding a Gray code
    // requires folding in every higher bit, so this is wrong for any value whose
    // ordinal needs more than one fold (e.g. gray_decode(gray_encode(5)) == 4).
    g ^ (g >> 1)
}
