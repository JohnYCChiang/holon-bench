use martial_crit::CritRoller;

#[test]
fn zero_chance_never_crits() {
    let mut r = CritRoller::new(42);
    for t in 0..50 {
        assert!(!r.is_crit(7, t, 0));
    }
}

#[test]
fn full_chance_always_crits() {
    let mut r = CritRoller::new(42);
    for t in 0..50 {
        assert!(r.is_crit(7, t, 100));
    }
}

#[test]
fn independent_of_prior_rolls() {
    // The same coordinates must resolve identically whether or not unrelated
    // rolls were processed first (a stateful roller diverges here).
    let coords: [(u64, u64); 6] = [(5, 20), (8, 3), (2, 9), (11, 11), (4, 40), (7, 1)];
    let mut clean = CritRoller::new(7);
    let base: Vec<bool> = coords.iter().map(|&(a, t)| clean.is_crit(a, t, 50)).collect();

    let mut noisy = CritRoller::new(7);
    noisy.is_crit(1, 1, 50);
    noisy.is_crit(2, 2, 50);
    noisy.is_crit(3, 3, 50);
    let after: Vec<bool> = coords.iter().map(|&(a, t)| noisy.is_crit(a, t, 50)).collect();

    assert_eq!(base, after, "crit decisions depend on call order");
}
