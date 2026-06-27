use hex_codec::{decode_hex, HexError};

#[test]
fn odd_length_is_error_not_panic() {
    assert_eq!(decode_hex("abc"), Err(HexError::OddLength));
}
