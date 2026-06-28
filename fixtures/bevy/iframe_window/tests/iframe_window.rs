use iframe_window::iframe::{apply_hit, is_invulnerable, start_dash, tick, IFrames};

#[test]
fn dash_negates_damage_while_invulnerable() {
    let mut f = IFrames::new();
    start_dash(&mut f, 0.5);
    assert!(is_invulnerable(&f));
    assert_eq!(apply_hit(&f, 25), 0);
}

#[test]
fn tick_clamps_remaining_at_zero() {
    let mut f = IFrames { remaining: 0.2 };
    tick(&mut f, 1.0);
    assert_eq!(f.remaining, 0.0);
    assert!(!is_invulnerable(&f));
    assert_eq!(apply_hit(&f, 25), 25);
}
