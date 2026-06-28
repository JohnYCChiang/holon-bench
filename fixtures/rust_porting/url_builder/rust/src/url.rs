fn enc(s: &str) -> String {
    let mut out = String::new();
    for b in s.bytes() {
        let c = b as char;
        if c.is_ascii_alphanumeric() || matches!(c, '_' | '.' | '-' | '~') {
            out.push(c);
        } else {
            out.push_str(&format!("%{:02X}", b));
        }
    }
    out
}

pub fn build_url(input: &str) -> String {
    let lines: Vec<&str> = input.split('\n').collect();
    let base = lines.first().copied().unwrap_or("");
    let mut params: Vec<(&str, &str)> = Vec::new();
    for line in &lines[1..] {
        if let Some((k, v)) = line.split_once('=') {
            params.push((k, v));
        }
    }
    let qs = params
        .iter()
        .map(|(k, v)| format!("{}={}", enc(k), enc(v)))
        .collect::<Vec<_>>()
        .join("&");
    if qs.is_empty() {
        base.to_string()
    } else {
        format!("{}?{}", base, qs)
    }
}
