use quote_balance::validate;

#[test]
fn escaped_quote_inside_string_is_literal() {
    // The text is the four characters: quote, backslash, quote, quote — a
    // double-quoted span containing one escaped (literal) quote.
    assert!(validate(r#""\"""#).is_ok());
}
