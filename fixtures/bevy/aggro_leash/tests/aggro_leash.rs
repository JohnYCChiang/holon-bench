use aggro_leash::leash::{decide, Vec2};

#[test]
fn chases_within_leash() {
    let home = Vec2::new(0.0, 0.0);
    let enemy = Vec2::new(3.0, 4.0); // dist 5 from home
    let target = Vec2::new(10.0, 10.0);
    assert_eq!(decide(home, enemy, target, 5.0), target);
}

#[test]
fn returns_home_when_beyond_leash() {
    let home = Vec2::new(0.0, 0.0);
    let enemy = Vec2::new(6.0, 8.0); // dist 10 from home
    let target = Vec2::new(6.0, 8.0); // target coincides with enemy
    assert_eq!(decide(home, enemy, target, 5.0), home);
}
