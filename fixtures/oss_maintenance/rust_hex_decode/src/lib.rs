//! Minimal ASCII hex codec. Two hex digits encode one byte, high nibble first.
//! Decoding accepts upper- and lower-case digits and must never panic: malformed
//! input is surfaced as a `HexError`.

#[derive(Debug, PartialEq, Eq)]
pub enum HexError {
    /// The input has an odd number of characters.
    OddLength,
    /// A non-hex character was encountered.
    InvalidChar(char),
}

/// Decode an ASCII hex string into bytes.
pub fn decode_hex(s: &str) -> Result<Vec<u8>, HexError> {
    let bytes = s.as_bytes();
    let mut out = Vec::with_capacity(bytes.len() / 2);
    let mut i = 0;
    while i < bytes.len() {
        // BUG: indexes bytes[i + 1] without an even-length check (panics on odd
        // length) and unwraps to_digit (panics on a non-hex character).
        let hi = (bytes[i] as char).to_digit(16).unwrap();
        let lo = (bytes[i + 1] as char).to_digit(16).unwrap();
        out.push((hi * 16 + lo) as u8);
        i += 2;
    }
    Ok(out)
}
