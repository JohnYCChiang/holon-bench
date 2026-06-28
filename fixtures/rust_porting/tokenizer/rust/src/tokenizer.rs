pub fn tokenize(input: &str) -> String {
    let mut s = input.to_string();
    if s.ends_with('\n') {
        s.pop();
    }
    let tokens: Vec<String> = s.split_whitespace().map(|t| t.to_string()).collect();
    format!("tokens={}", tokens.join("|"))
}
