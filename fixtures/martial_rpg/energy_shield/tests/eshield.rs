use martial_eshield::{absorb, Defense};

#[test]
fn shield_absorbs_first() {
    let d = Defense { shield: 50, hp: 100 };
    assert_eq!(absorb(&d, 30), (20, 100));
}

#[test]
fn overflow_spills_to_hp() {
    let d = Defense { shield: 20, hp: 100 };
    assert_eq!(absorb(&d, 50), (0, 70));
}

#[test]
fn exact_shield_leaves_hp_intact() {
    let d = Defense { shield: 30, hp: 100 };
    assert_eq!(absorb(&d, 30), (0, 100));
}
