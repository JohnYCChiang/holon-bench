use ability_cooldown::cooldown::{is_ready, tick, trigger, Cooldown};

#[test]
fn tick_clamps_remaining_at_zero() {
    let mut cd = Cooldown { remaining: 0.5, duration: 2.0 };
    tick(&mut cd, 0.8);
    assert_eq!(cd.remaining, 0.0);
    assert!(is_ready(&cd));
}

#[test]
fn trigger_rearms_to_full_duration() {
    let mut cd = Cooldown::new(2.0);
    assert!(trigger(&mut cd));
    assert_eq!(cd.remaining, 2.0);
    assert!(!trigger(&mut cd));
}
