use cow_normalize::text::normalize;
use std::borrow::Cow;

#[test]
fn replaces_tabs() {
    assert_eq!(&*normalize("a\tb"), "a    b");
}

#[test]
fn borrowed_when_no_tab() {
    assert!(matches!(normalize("clean"), Cow::Borrowed(_)));
}
