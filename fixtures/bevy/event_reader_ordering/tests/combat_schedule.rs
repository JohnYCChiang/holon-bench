use event_reader_ordering::plugins::combat::run_combat_frame;
use event_reader_ordering::systems::combat::{emit_damage, World};

#[test]
fn combat_schedule_applies_damage_before_collecting_deaths() {
    let mut world = World {
        health: vec![(7, 3)],
        pending_damage: Vec::new(),
        deaths: Vec::new(),
    };
    emit_damage(&mut world, 7, 5);

    run_combat_frame(&mut world);

    assert_eq!(world.health, vec![(7, -2)]);
    assert_eq!(world.deaths, vec![7]);
}
