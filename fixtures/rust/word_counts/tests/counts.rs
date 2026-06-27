use std::collections::BTreeMap;

use word_counts::counts::word_counts;

#[test]
fn counts_repeated_words() {
    let got = word_counts("a b a c a b");
    let expected: BTreeMap<String, usize> =
        [("a", 3), ("b", 2), ("c", 1)].iter().map(|(k, v)| (k.to_string(), *v)).collect();
    assert_eq!(got, expected);
}

#[test]
fn empty_text_is_empty_map() {
    assert!(word_counts("").is_empty());
}
