use base62_codec::encode;

#[test]
fn multi_digit_is_most_significant_first() {
    assert_eq!(encode(62), "10");
}
