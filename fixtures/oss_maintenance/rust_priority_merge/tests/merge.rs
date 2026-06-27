use priority_merge::merge_k;

#[test]
fn all_elements_survive() {
    let lists = vec![vec![(1, 0), (3, 0)], vec![(2, 1)]];
    assert_eq!(merge_k(lists), vec![(1, 0), (2, 1), (3, 0)]);
}
