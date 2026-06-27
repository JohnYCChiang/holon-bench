//! Parse a `key=value` line, splitting on the first `=`. Malformed input must be
//! reported as an `Err`, never a panic.

#[derive(Debug, PartialEq, Eq)]
pub enum ParseError {
    /// The line contained no `=` delimiter.
    MissingDelimiter,
    /// The key (text before the first `=`) was empty.
    EmptyKey,
}

/// Parse `line` into `(key, value)`. The split happens on the FIRST `=`, so the
/// value may itself contain `=` characters.
pub fn parse_kv(line: &str) -> Result<(String, String), ParseError> {
    let idx = line.find('=').unwrap(); // BUG: panics when '=' is absent
    let (key, rest) = line.split_at(idx);
    let value = &rest[1..]; // skip the '=' delimiter
    if key.is_empty() {
        return Err(ParseError::EmptyKey);
    }
    Ok((key.to_string(), value.to_string()))
}
