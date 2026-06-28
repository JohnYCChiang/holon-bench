use lifesteal_cap::lifesteal::{apply_lifesteal, Fighter};

#[test]
fn heal_is_capped_at_max() {
    let mut f = Fighter::new(90, 100);
    apply_lifesteal(&mut f, 100, 50); // +50 -> capped to 100
    assert_eq!(f.hp, 100);
}

#[test]
fn partial_heal_below_max() {
    let mut f = Fighter::new(50, 100);
    apply_lifesteal(&mut f, 40, 50); // +20
    assert_eq!(f.hp, 70);
}
