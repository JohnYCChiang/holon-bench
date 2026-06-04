use health_component::components::HealthBundle;
use health_component::systems::health::apply_damage;

#[test]
fn mutation_negative_damage_cannot_heal_or_exceed_max_health() {
    let mut bundle = HealthBundle::new(10);
    bundle.health.current = 6;

    let result = apply_damage(&mut bundle.health, -20);

    assert_eq!(bundle.health.current, 6);
    assert_eq!(result.remaining, 6);
    assert!(!result.died);
    assert!(bundle.health.current <= bundle.health.max);
}
