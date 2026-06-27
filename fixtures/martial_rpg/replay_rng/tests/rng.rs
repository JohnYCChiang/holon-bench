use martial_rng::ReplayRng;

#[test]
fn roll_is_pure_for_coordinates() {
    let mut a = ReplayRng::new(42);
    let mut b = ReplayRng::new(42);
    assert_eq!(a.roll_for(1, 5), b.roll_for(1, 5));
}

#[test]
fn order_does_not_affect_rolls() {
    let mut forward = ReplayRng::new(99);
    let f1 = forward.roll_for(1, 10);
    let f2 = forward.roll_for(2, 20);

    let mut reversed = ReplayRng::new(99);
    let r2 = reversed.roll_for(2, 20);
    let r1 = reversed.roll_for(1, 10);

    assert_eq!(f1, r1);
    assert_eq!(f2, r2);
}
