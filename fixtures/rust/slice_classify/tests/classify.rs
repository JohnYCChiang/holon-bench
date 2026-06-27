use slice_classify::classify::{summarize, Summary};

#[test]
fn empty_and_single() {
    assert_eq!(summarize(&[]), Summary::Empty);
    assert_eq!(summarize(&[7]), Summary::Single(7));
}

#[test]
fn pair_and_span() {
    assert_eq!(summarize(&[1, 2]), Summary::Pair(1, 2));
    assert_eq!(
        summarize(&[1, 2, 3]),
        Summary::Span { first: 1, last: 3, len: 3 }
    );
}
