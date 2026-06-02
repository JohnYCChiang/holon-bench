pub fn compact(text: &str, limit: usize) -> (usize, String) {
    let lines: Vec<&str> = text.lines().collect();
    (0, lines.join("|"))
}
