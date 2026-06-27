use lower_bound::lower_bound;

#[test]
fn first_occurrence_of_duplicate() {
    assert_eq!(lower_bound(&[1, 2, 2, 2, 3], 2), 1);
}
