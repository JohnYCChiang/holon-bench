use parry_window::parry::{parries, ParryTiming};

#[test]
fn attack_inside_window_is_parried() {
    let timing = ParryTiming::new(0.5, 0.25);
    assert!(parries(&timing, 0.625));
}

#[test]
fn attack_before_startup_is_not_parried() {
    let timing = ParryTiming::new(0.5, 0.25);
    assert!(!parries(&timing, 0.125));
}
