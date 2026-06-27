use std::convert::TryFrom;

#[derive(Debug, PartialEq, Eq, Clone, Copy)]
pub struct Rgb {
    pub r: u8,
    pub g: u8,
    pub b: u8,
}

#[derive(Debug, PartialEq, Eq)]
pub enum ParseColorError {
    MissingHash,
    BadLength,
    InvalidDigit,
}

impl TryFrom<&str> for Rgb {
    type Error = ParseColorError;

    fn try_from(value: &str) -> Result<Self, Self::Error> {
        // BROKEN: ignores all validation and parsing.
        Ok(Rgb { r: 0, g: 0, b: 0 })
    }
}
