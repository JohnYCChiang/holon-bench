pub fn format_logs(input: &str) -> String {
    let mut out: Vec<String> = Vec::new();
    for line in input.split('\n') {
        if line.trim().is_empty() {
            continue;
        }
        let pos = match line.rfind(':') {
            Some(p) => p,
            None => continue,
        };
        let level = line[..pos].trim().to_string();
        let msg = line[pos + 1..].trim();
        out.push(format!("{} {}", level, msg));
    }
    out.join("\n")
}
