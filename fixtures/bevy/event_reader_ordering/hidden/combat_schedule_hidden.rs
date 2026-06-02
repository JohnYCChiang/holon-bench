use event_reader_ordering::plugins::combat::run_combat_frame;
use event_reader_ordering::systems::combat::{emit_damage, World};

#[test]
fn hidden_frame_applies_all_damage_before_collecting_deaths() {
    let mut world = World {
        health: vec![(1, 10), (2, 4), (3, 8)],
        pending_damage: Vec::new(),
        deaths: Vec::new(),
    };

    emit_damage(&mut world, 1, 3);
    emit_damage(&mut world, 2, 4);
    emit_damage(&mut world, 3, 9);

    run_combat_frame(&mut world);

    assert_eq!(world.health, vec![(1, 7), (2, 0), (3, -1)]);
    assert_eq!(world.deaths, vec![2, 3]);
    assert!(world.pending_damage.is_empty());
}

#[test]
fn hidden_later_frames_do_not_duplicate_existing_deaths() {
    let mut world = World {
        health: vec![(10, 1), (20, 5)],
        pending_damage: Vec::new(),
        deaths: Vec::new(),
    };

    emit_damage(&mut world, 10, 2);
    run_combat_frame(&mut world);
    assert_eq!(world.deaths, vec![10]);

    emit_damage(&mut world, 20, 6);
    run_combat_frame(&mut world);

    assert_eq!(world.health, vec![(10, -1), (20, -1)]);
    assert_eq!(world.deaths, vec![10, 20]);
}
