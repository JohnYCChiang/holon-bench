#[derive(Debug, PartialEq, Eq)]
pub struct ToolError {
    pub code: &'static str,
    pub retryable: bool,
}

pub fn classify(kind: &str) -> ToolError {
    match kind {
        "timeout" => ToolError { code: "timeout", retryable: false },
        "validation" => ToolError { code: "validation", retryable: false },
        _ => ToolError { code: "unknown", retryable: false },
    }
}
