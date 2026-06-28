pub fn render(input: &str) -> String {
    let lines: Vec<&str> = input.split('\n').collect();
    let template = lines.first().copied().unwrap_or("");
    let mut result = template.to_string();
    for line in &lines[1..] {
        if line.is_empty() {
            continue;
        }
        if let Some(p) = line.find('=') {
            let k = &line[..p];
            let v = &line[p + 1..];
            result = result.replace(&format!("{{{{{}}}}}", k), v);
        }
    }
    format!("rendered={}", result)
}
