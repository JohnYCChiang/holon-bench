/// Return the second whitespace-separated word, if present.
pub fn second_word(s: &str) -> Option<&str> {
    // BROKEN: returns the first word instead of the second.
    s.split_whitespace().next()
}
