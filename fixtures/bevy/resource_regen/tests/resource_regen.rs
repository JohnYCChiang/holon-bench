use resource_regen::regen::{regen, Pool};

#[test]
fn caps_at_max() {
    let mut p = Pool::new(95, 100);
    regen(&mut p, 10.0, 1.0); // +10 -> capped at 100
    assert_eq!(p.current, 100);
    assert_eq!(p.accum, 0.0);
}

#[test]
fn accumulates_fractional() {
    let mut p = Pool::new(0, 100);
    regen(&mut p, 1.0, 0.5); // 0.5 progress, no whole point
    assert_eq!(p.current, 0);
    assert!((p.accum - 0.5).abs() < 1e-6);
}
