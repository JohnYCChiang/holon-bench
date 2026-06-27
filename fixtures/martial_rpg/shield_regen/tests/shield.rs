use martial_shield::Shield;

#[test]
fn damage_never_underflows() {
    let mut s = Shield::new(50, 5, 3);
    s.take_damage(80); // more than current; must clamp at 0, not underflow
    assert_eq!(s.current, 0);
}

#[test]
fn regen_does_not_exceed_max() {
    let mut s = Shield::new(50, 5, 0); // no delay
    s.current = 48;
    s.tick();
    assert_eq!(s.current, 50);
}

#[test]
fn regen_paused_during_delay() {
    let mut s = Shield::new(50, 5, 2);
    s.take_damage(20); // current 30, delay_remaining = 2
    s.tick(); // delay tick, no regen
    assert_eq!(s.current, 30);
}
