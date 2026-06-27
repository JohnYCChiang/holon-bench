//! Parse an integer in an arbitrary radix (2..=36) into an `i64`. A leading
//! `+`/`-` sign is allowed and digits are case-insensitive. Malformed input is
//! surfaced as a `ParseError`; the parser must never panic.

#[derive(Debug, PartialEq, Eq)]
pub enum ParseError {
    /// The radix is outside the supported 2..=36 range.
    BadRadix,
    /// The input had no digits (empty, or only a sign).
    Empty,
    /// A character that is not a valid digit for the radix.
    InvalidDigit(char),
    /// The parsed value does not fit in an i64.
    Overflow,
}

/// Parse `s` as an integer in `radix`.
pub fn parse_radix(s: &str, radix: u32) -> Result<i64, ParseError> {
    let mut result: i64 = 0;
    for c in s.chars() {
        // BUG: unwraps to_digit (panics on the sign char and on any non-digit),
        // ignores the sign entirely, and never checks for i64 overflow.
        let d = c.to_digit(radix).unwrap();
        result = result * (radix as i64) + d as i64;
    }
    Ok(result)
}
