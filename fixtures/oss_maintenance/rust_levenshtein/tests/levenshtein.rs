use levenshtein::distance;

#[test]
fn multibyte_char_is_one_edit() {
    assert_eq!(distance("café", "cafe"), 1);
}
