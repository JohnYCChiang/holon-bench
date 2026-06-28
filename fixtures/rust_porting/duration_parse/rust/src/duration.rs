pub fn parse_duration(input: &str) -> String {
    let s = input.trim();
    if s.is_empty() {
        return "error=invalid".to_string();
    }
    let chars: Vec<char> = s.chars().collect();
    let n = chars.len();
    let mut pos = 0;
    let mut total: i64 = 0;
    while pos < n {
        let start = pos;
        while pos < n && chars[pos].is_ascii_digit() {
            pos += 1;
        }
        if pos == start {
            return "error=invalid".to_string();
        }
        let num: i64 = chars[start..pos].iter().collect::<String>().parse().unwrap();
        if pos >= n {
            return "error=invalid".to_string();
        }
        let mult = match chars[pos] {
            'h' => 3600,
            'm' => 60,
            's' => 1,
            _ => return "error=invalid".to_string(),
        };
        total += num * mult;
        pos += 1;
    }
    format!("seconds={}", total)
}
