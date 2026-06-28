use std::collections::HashMap;

pub fn expand(input: &str) -> String {
    let (header, body) = match input.split_once("\n--\n") {
        Some((h, b)) => (h, b),
        None => ("", input),
    };
    let mut env: HashMap<String, String> = HashMap::new();
    for line in header.split('\n') {
        if let Some((k, v)) = line.split_once('=') {
            env.insert(k.to_string(), v.to_string());
        }
    }
    let chars: Vec<char> = body.chars().collect();
    let mut out = String::new();
    let mut i = 0;
    while i < chars.len() {
        if chars[i] == '$' {
            if i + 1 < chars.len() && chars[i + 1] == '$' {
                out.push('$');
                i += 2;
                continue;
            }
            let mut j = i + 1;
            let mut name = String::new();
            while j < chars.len() && (chars[j].is_alphanumeric() || chars[j] == '_') {
                name.push(chars[j]);
                j += 1;
            }
            if name.is_empty() {
                out.push('$');
                i += 1;
                continue;
            }
            out.push_str(env.get(&name).map(|s| s.as_str()).unwrap_or(""));
            i = j;
            continue;
        }
        out.push(chars[i]);
        i += 1;
    }
    out
}
