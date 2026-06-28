pub fn classify(input: &str) -> String {
    let mut out: Vec<String> = Vec::new();
    for line in input.split('\n') {
        let line = line.trim();
        if line.is_empty() {
            continue;
        }
        match line.parse::<i64>() {
            Err(_) => out.push(format!("{}=error", line)),
            Ok(code) => {
                let d = if (200..=399).contains(&code) {
                    "ok"
                } else if (400..=499).contains(&code) {
                    "fail"
                } else if (500..=599).contains(&code) {
                    "retry"
                } else {
                    "error"
                };
                out.push(format!("{}={}", code, d));
            }
        }
    }
    out.join(";")
}
