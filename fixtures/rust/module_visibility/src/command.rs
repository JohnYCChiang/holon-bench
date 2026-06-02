#[derive(Debug, PartialEq, Eq)]
pub struct Command {
    pub name: String,
    pub args: Vec<String>,
}

pub fn parse_command(input: &str) -> Command {
    crate::internal::parse(input)
}
