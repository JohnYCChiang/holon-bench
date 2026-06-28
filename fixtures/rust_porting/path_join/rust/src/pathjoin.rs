pub fn join_paths(input: &str) -> String {
    let parts: Vec<&str> = input.split('\n').collect();
    parts.join("/")
}
