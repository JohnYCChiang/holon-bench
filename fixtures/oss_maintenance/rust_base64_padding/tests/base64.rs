use base64_pad::encode;

#[test]
fn single_byte_is_padded() {
    assert_eq!(encode(b"M"), "TQ==");
}
