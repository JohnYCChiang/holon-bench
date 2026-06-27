use radix_parse::parse_radix;

#[test]
fn negative_binary_is_parsed_not_panicked() {
    assert_eq!(parse_radix("-101", 2), Ok(-5));
}
