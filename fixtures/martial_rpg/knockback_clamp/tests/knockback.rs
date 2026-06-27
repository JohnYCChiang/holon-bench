use martial_knockback::{apply_knockback, Arena};

#[test]
fn impulse_clamped_per_axis() {
    let a = Arena { width: 100, height: 100 };
    let p = apply_knockback((50, 50), (40, -40), 10, &a);
    assert_eq!(p, (60, 40)); // each axis impulse clamped to +/-10
}

#[test]
fn position_clamped_to_arena() {
    let a = Arena { width: 20, height: 20 };
    let p = apply_knockback((18, 2), (10, -10), 10, &a);
    assert_eq!(p, (20, 0));
}

#[test]
fn small_impulse_preserved() {
    let a = Arena { width: 100, height: 100 };
    let p = apply_knockback((50, 50), (3, -4), 10, &a);
    assert_eq!(p, (53, 46));
}
