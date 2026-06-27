use martial_combat::Combatant;

#[test]
fn tick_does_not_underflow_cooldown() {
    let mut c = Combatant::new(100);
    // cooldown is already 0; ticking must not panic and must stay at 0.
    c.tick();
    assert_eq!(c.cooldown, 0);
}

#[test]
fn stamina_regen_is_capped() {
    let mut c = Combatant::new(100);
    c.stamina = 98;
    c.tick();
    assert_eq!(c.stamina, 100);
}
