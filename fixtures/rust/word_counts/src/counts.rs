use std::collections::BTreeMap;

/// Count occurrences of each whitespace-separated word.
pub fn word_counts(text: &str) -> BTreeMap<String, usize> {
    let mut map = BTreeMap::new();
    for word in text.split_whitespace() {
        // BROKEN: overwrites the count instead of accumulating it.
        map.insert(word.to_string(), 1);
    }
    map
}
