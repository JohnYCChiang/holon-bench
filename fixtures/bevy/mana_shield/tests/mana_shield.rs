use mana_shield::shield::{absorb, Shield};

#[test]
fn mana_absorbs_before_health() {
    let mut s = Shield { mana: 10, health: 30 };
    absorb(&mut s, 4);
    assert_eq!(s.mana, 6);
    assert_eq!(s.health, 30);
}

#[test]
fn overflow_spills_to_health() {
    let mut s = Shield { mana: 5, health: 30 };
    absorb(&mut s, 8);
    assert_eq!(s.mana, 0);
    assert_eq!(s.health, 27);
}
