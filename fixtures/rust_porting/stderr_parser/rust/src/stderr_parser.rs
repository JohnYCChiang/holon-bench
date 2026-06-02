pub fn parse_stderr(text: &str) -> String {
    format!("errors=0;warnings=0;first={}", text.lines().next().unwrap_or(""))
}
