use martial_mitigation::{mitigate, Mitigation};

#[test]
fn armor_is_applied_before_resist() {
    // raw 100, armor 20 -> 80, then 50% resist -> 40
    let out = mitigate(100, Mitigation { armor: 20, resist_pct: 50 });
    assert_eq!(out, 40);
}

#[test]
fn over_armored_floors_at_zero() {
    let out = mitigate(10, Mitigation { armor: 100, resist_pct: 0 });
    assert_eq!(out, 0);
}
