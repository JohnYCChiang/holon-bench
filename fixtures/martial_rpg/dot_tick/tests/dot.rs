use martial_dot::Dot;

#[test]
fn damage_lands_on_period_boundary() {
    let mut d = Dot::new(3, 2, 5);
    let hp = d.step(100); // tick 1: no application
    assert_eq!(hp, 100);
    assert_eq!(d.remaining(), 3);
    let hp = d.step(hp); // tick 2: application
    assert_eq!(hp, 95);
    assert_eq!(d.remaining(), 2);
}

#[test]
fn no_damage_between_periods() {
    let mut d = Dot::new(3, 4, 7);
    let hp = d.step(50);
    assert_eq!(hp, 50);
    assert_eq!(d.remaining(), 3);
}

#[test]
fn clamps_hp_at_zero() {
    let mut d = Dot::new(10, 1, 50);
    let mut hp = 30;
    hp = d.step(hp); // 30 -> 0 (saturating)
    assert_eq!(hp, 0);
    hp = d.step(hp); // stays at 0, no underflow
    assert_eq!(hp, 0);
}
