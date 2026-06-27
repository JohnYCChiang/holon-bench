use damage_resolution::combat::{apply, resolve_damage};

#[test]
fn heavy_armor_still_takes_chip_damage() {
    // Raw 5 vs armor 10 would be -5, but a positive hit must chip for 1.
    assert_eq!(resolve_damage(5, 10), 1);
}

#[test]
fn applied_damage_never_drops_below_zero_hp() {
    let dmg = resolve_damage(40, 5);
    assert_eq!(dmg, 35);
    assert_eq!(apply(20, dmg), 0);
}
