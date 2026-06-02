use typed_error_propagation::{parse_entry, ParseError};

#[test]
fn parser_errors_are_typed_and_never_panic() {
    assert_eq!(parse_entry("count:42").unwrap().value, 42);
    assert_eq!(parse_entry("missing_separator"), Err(ParseError::MissingSeparator));
    assert_eq!(parse_entry(":12"), Err(ParseError::EmptyKey));
    assert_eq!(parse_entry("count:not-a-number"), Err(ParseError::InvalidNumber));
}
