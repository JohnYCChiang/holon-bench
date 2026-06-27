//! Validate that brackets `() [] {}` are balanced in a string, where bracket
//! characters inside a double-quoted span are literal and ignored, and a
//! backslash inside a quoted span escapes the next character.

#[derive(Debug, PartialEq, Eq)]
pub enum QuoteError {
    /// A closing bracket with no matching open, or a mismatched pair.
    UnexpectedClose,
    /// One or more open brackets were never closed.
    UnclosedBracket,
    /// A double-quoted span was opened but never closed.
    UnterminatedString,
}

/// Return Ok(()) if `s` is balanced, else the first violation.
pub fn validate(s: &str) -> Result<(), QuoteError> {
    let chars: Vec<char> = s.chars().collect();
    let mut stack: Vec<char> = Vec::new();
    let mut in_str = false;
    let mut i = 0;
    while i < chars.len() {
        let c = chars[i];
        if in_str {
            // BUG: inside a quoted span a backslash must escape the next
            // character (so `\"` is a literal quote, not a terminator). That
            // escape handling is missing, so escaped quotes corrupt the parse.
            if c == '"' {
                in_str = false;
            }
        } else {
            match c {
                '"' => in_str = true,
                '(' | '[' | '{' => stack.push(c),
                ')' | ']' | '}' => {
                    let open = match c {
                        ')' => '(',
                        ']' => '[',
                        _ => '{',
                    };
                    if stack.pop() != Some(open) {
                        return Err(QuoteError::UnexpectedClose);
                    }
                }
                _ => {}
            }
        }
        i += 1;
    }
    if in_str {
        return Err(QuoteError::UnterminatedString);
    }
    if !stack.is_empty() {
        return Err(QuoteError::UnclosedBracket);
    }
    Ok(())
}
