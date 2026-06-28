use knockback_friction::knockback::{apply_friction, Velocity};

#[test]
fn friction_reduces_speed() {
    let mut v = Velocity { vx: 3.0, vy: 4.0 };
    apply_friction(&mut v, 1.0, 1.0);
    assert!((v.vx - 2.4).abs() < 1e-5);
    assert!((v.vy - 3.2).abs() < 1e-5);
}

#[test]
fn large_friction_snaps_to_zero() {
    let mut v = Velocity { vx: 3.0, vy: 4.0 };
    apply_friction(&mut v, 100.0, 1.0);
    assert_eq!(v.vx, 0.0);
    assert_eq!(v.vy, 0.0);
}
