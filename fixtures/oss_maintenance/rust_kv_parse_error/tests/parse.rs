use kv_parse::{parse_kv, ParseError};

#[test]
fn missing_delimiter_is_an_error_not_a_panic() {
    assert_eq!(parse_kv("noeq"), Err(ParseError::MissingDelimiter));
}

#[test]
fn basic_pair_parses() {
    assert_eq!(parse_kv("k=v"), Ok(("k".to_string(), "v".to_string())));
}
