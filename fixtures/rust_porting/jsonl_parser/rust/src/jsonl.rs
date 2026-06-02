pub fn parse_jsonl(text: &str) -> (Vec<String>, Vec<usize>) {
    let records = text.lines().map(|line| line.to_string()).collect();
    (records, Vec::new())
}
