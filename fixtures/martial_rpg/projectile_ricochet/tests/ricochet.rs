use martial_ricochet::ricochet_chain;

#[test]
fn hops_to_successive_nearest_targets() {
    // origin at 0; targets along the x-axis.
    let targets = [(1, 0), (2, 0), (10, 0), (3, 0)];
    let chain = ricochet_chain((0, 0), &targets, 2, 3);
    assert_eq!(chain, vec![0, 1, 3]);
}

#[test]
fn nothing_in_range_yields_empty() {
    let targets = [(5, 5)];
    let chain = ricochet_chain((0, 0), &targets, 2, 5);
    assert!(chain.is_empty());
}

#[test]
fn each_target_hit_at_most_once() {
    let targets = [(1, 0)];
    let chain = ricochet_chain((0, 0), &targets, 5, 10);
    assert_eq!(chain, vec![0]);
}
