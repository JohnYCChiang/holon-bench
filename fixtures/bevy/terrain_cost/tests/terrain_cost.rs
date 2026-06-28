use terrain_cost::terrain::reachable_steps;

#[test]
fn stops_before_exceeding_budget() {
    assert_eq!(reachable_steps(&[2, 2, 2], 3), 1);
}

#[test]
fn spends_exact_budget() {
    assert_eq!(reachable_steps(&[1, 2], 3), 2);
}
