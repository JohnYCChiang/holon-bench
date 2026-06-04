use health_component::components::HealthBundle;
use health_component::systems::health::{apply_damage, is_alive};

#[test]
fn hidden_zero_damage_preserves_health() {
    let mut bundle = HealthBundle::new(10);
    let result = apply_damage(&mut bundle.health, 0);

    assert_eq!(bundle.health.current, 10);
    assert_eq!(result.remaining, 10);
    assert!(!result.died);
    assert!(is_alive(&bundle.health));
}
