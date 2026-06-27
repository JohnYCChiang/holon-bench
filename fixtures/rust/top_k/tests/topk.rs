use top_k::topk::top_k;

#[test]
fn picks_largest_descending() {
    assert_eq!(top_k(&[3, 1, 4, 1, 5, 9, 2, 6], 3), vec![9, 6, 5]);
}

#[test]
fn zero_k_is_empty() {
    assert_eq!(top_k(&[1, 2, 3], 0), Vec::<i64>::new());
}
