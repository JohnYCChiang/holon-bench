use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize)]
pub struct ToolRequest {
    pub root: String,
    pub include_hidden: Option<bool>,
}

#[derive(Debug, PartialEq, Serialize)]
pub struct ToolResponse {
    pub ok: bool,
    pub root: String,
    pub include_hidden: bool,
}

pub fn run(request: ToolRequest) -> ToolResponse {
    ToolResponse {
        ok: true,
        root: request.root,
        include_hidden: request.include_hidden.unwrap_or(false),
    }
}
