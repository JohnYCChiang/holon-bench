pub fn write_row(input: &str) -> String {
    input
        .split('\n')
        .map(|f| {
            if f.contains(',') || f.contains('"') {
                format!("\"{}\"", f)
            } else {
                f.to_string()
            }
        })
        .collect::<Vec<_>>()
        .join(",")
}
