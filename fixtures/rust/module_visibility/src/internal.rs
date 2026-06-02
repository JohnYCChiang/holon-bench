use crate::command::Command;

pub fn parse(input: &str) -> Command {
    let mut parts = input.split_whitespace();
    Command {
        name: parts.next().unwrap_or_default().to_string(),
        args: parts.map(str::to_string).collect(),
    }
}
