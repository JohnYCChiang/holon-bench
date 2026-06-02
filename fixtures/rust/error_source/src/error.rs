use std::fmt;
use std::io;

#[derive(Debug)]
pub enum ToolError {
    Io,
}

impl fmt::Display for ToolError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ToolError::Io => write!(formatter, "io failure"),
        }
    }
}

impl std::error::Error for ToolError {}

impl From<io::Error> for ToolError {
    fn from(_value: io::Error) -> Self {
        ToolError::Io
    }
}
