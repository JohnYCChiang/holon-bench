use health_component::components::HealthBundle;
use health_component::systems::health::{apply_damage, is_alive};

#[test]
fn health_logic_clamps_damage_without_component_behavior() {
    let mut bundle = HealthBundle::new(10);
    let result = apply_damage(&mut bundle.health, 4);

    assert_eq!(bundle.health.current, 6);
    assert_eq!(result.remaining, 6);
    assert!(!result.died);
    assert!(is_alive(&bundle.health));
}

#[test]
fn health_logic_reports_death_once_health_reaches_zero() {
    let mut bundle = HealthBundle::new(5);
    let result = apply_damage(&mut bundle.health, 99);

    assert_eq!(bundle.health.current, 0);
    assert_eq!(result.remaining, 0);
    assert!(result.died);
    assert!(!is_alive(&bundle.health));
}
