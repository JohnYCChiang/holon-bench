#[derive(Debug, PartialEq, Eq, Clone, Copy)]
pub struct Percentage(u8);

#[derive(Debug, PartialEq, Eq)]
pub struct OutOfRange(pub u16);

impl Percentage {
    pub fn new(value: u16) -> Result<Percentage, OutOfRange> {
        // BROKEN: truncates instead of validating the 0..=100 invariant.
        Ok(Percentage(value as u8))
    }

    pub fn value(&self) -> u8 {
        self.0
    }
}
