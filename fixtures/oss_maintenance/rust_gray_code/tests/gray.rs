use gray_code::{gray_decode, gray_encode};

#[test]
fn roundtrip_needs_multiple_folds() {
    assert_eq!(gray_decode(gray_encode(5)), 5);
}
