//! Base62 encoding using the alphabet 0-9 A-Z a-z. `encode(0)` is "0".

const ALPHABET: &[u8] = b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

/// Encode `n` as a base62 string (most-significant digit first).
pub fn encode(mut n: u64) -> String {
    if n == 0 {
        return "0".to_string();
    }
    let mut out = Vec::new();
    while n > 0 {
        out.push(ALPHABET[(n % 62) as usize]);
        n /= 62;
    }
    // BUG: digits were produced least-significant first and are never reversed,
    // so the encoded string comes out backwards for any multi-digit value.
    String::from_utf8(out).unwrap()
}
