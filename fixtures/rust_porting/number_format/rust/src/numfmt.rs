pub fn format_number(input: &str) -> String {
    let raw = input.trim();
    let digits: &str = raw.trim_start_matches(['+', '-']);
    if digits.is_empty() || !digits.chars().all(|c| c.is_ascii_digit()) {
        return "error".to_string();
    }
    let trimmed = digits.trim_start_matches('0');
    let s = if trimmed.is_empty() { "0" } else { trimmed };
    let bytes = s.as_bytes();
    let mut parts: Vec<String> = Vec::new();
    let mut end = bytes.len();
    while end > 3 {
        parts.push(String::from_utf8(bytes[end - 3..end].to_vec()).unwrap());
        end -= 3;
    }
    parts.push(String::from_utf8(bytes[0..end].to_vec()).unwrap());
    parts.reverse();
    parts.join(",")
}
