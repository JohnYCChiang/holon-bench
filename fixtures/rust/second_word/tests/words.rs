use second_word::words::second_word;

#[test]
fn returns_second_word() {
    assert_eq!(second_word("hello world foo"), Some("world"));
}

#[test]
fn none_when_only_one_word() {
    assert_eq!(second_word("lonely"), None);
}

#[test]
fn none_when_empty() {
    assert_eq!(second_word(""), None);
}
