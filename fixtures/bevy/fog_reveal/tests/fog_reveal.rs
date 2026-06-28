use fog_reveal::fog::FogMap;

#[test]
fn reveal_marks_radius_inclusive() {
    let mut m = FogMap::new(5, 5);
    m.reveal(2, 2, 1);
    assert_eq!(m.explored_count(), 9);
    assert!(m.is_explored(1, 1));
    assert!(m.is_explored(3, 3));
    assert!(!m.is_explored(0, 0));
}

#[test]
fn reveal_is_cumulative() {
    let mut m = FogMap::new(5, 5);
    m.reveal(0, 0, 0);
    m.reveal(4, 4, 0);
    assert!(m.is_explored(0, 0), "earlier reveal must persist");
    assert!(m.is_explored(4, 4));
}
