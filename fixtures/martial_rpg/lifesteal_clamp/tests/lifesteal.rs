use martial_lifesteal::{lifesteal, Combatant};

#[test]
fn heals_a_fraction_of_damage() {
    let c = Combatant { hp: 50, max_hp: 100 };
    // 25% of 40 = 10
    assert_eq!(lifesteal(&c, 40, 25), 60);
}

#[test]
fn heal_is_capped_at_max_hp() {
    let c = Combatant { hp: 90, max_hp: 100 };
    // 100% of 50 = 50, but capped at max_hp
    assert_eq!(lifesteal(&c, 50, 100), 100);
}

#[test]
fn percentage_is_clamped_to_100() {
    let c = Combatant { hp: 0, max_hp: 1000 };
    // pct over 100 is clamped to 100: 100% of 30 = 30
    assert_eq!(lifesteal(&c, 30, 250), 30);
}
