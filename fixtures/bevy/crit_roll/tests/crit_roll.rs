use crit_roll::crit::{is_crit, resolve};

#[test]
fn roll_equal_to_chance_is_not_crit() {
    assert!(!is_crit(25, 25));
    assert_eq!(resolve(100, 25, 25, 200), 100);
}

#[test]
fn roll_below_chance_crits() {
    assert!(is_crit(10, 25));
    assert_eq!(resolve(100, 10, 25, 200), 200);
}
