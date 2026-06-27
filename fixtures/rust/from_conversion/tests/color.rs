use std::convert::TryFrom;
use from_conversion::color::{ParseColorError, Rgb};

#[test]
fn parses_valid_lowercase_hex() {
    assert_eq!(Rgb::try_from("#0a0b0c"), Ok(Rgb { r: 10, g: 11, b: 12 }));
}

#[test]
fn parses_white() {
    assert_eq!(Rgb::try_from("#ffffff"), Ok(Rgb { r: 255, g: 255, b: 255 }));
}

#[test]
fn rejects_missing_hash() {
    assert_eq!(Rgb::try_from("0a0b0c"), Err(ParseColorError::MissingHash));
}

#[test]
fn rejects_bad_length() {
    assert_eq!(Rgb::try_from("#0a0b"), Err(ParseColorError::BadLength));
}

#[test]
fn rejects_invalid_digit() {
    assert_eq!(Rgb::try_from("#0a0b0z"), Err(ParseColorError::InvalidDigit));
}
