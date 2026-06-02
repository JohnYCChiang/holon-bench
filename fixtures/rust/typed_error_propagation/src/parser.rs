use crate::ParseError;

#[derive(Debug, PartialEq, Eq)]
pub struct Entry {
    pub key: String,
    pub value: u32,
}

pub fn parse_entry(input: &str) -> Result<Entry, ParseError> {
    let (key, value) = input.split_once(':').unwrap();
    Ok(Entry {
        key: key.to_string(),
        value: value.parse::<u32>().unwrap(),
    })
}
