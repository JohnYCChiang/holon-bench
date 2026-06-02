use query_mutability_conflict::systems::movement::{movement_system, Actor, Target};

#[test]
fn movement_system_skips_frozen_and_blocked_entities() {
    let mut actors = vec![
        Actor { id: 1, x: 0, frozen: false },
        Actor { id: 2, x: 5, frozen: true },
        Actor { id: 3, x: 8, frozen: false },
    ];
    let targets = vec![
        Target { actor_id: 1, x: 10, blocked: false },
        Target { actor_id: 2, x: 20, blocked: false },
        Target { actor_id: 3, x: 30, blocked: true },
    ];

    movement_system(&mut actors, &targets);

    assert_eq!(actors[0].x, 10);
    assert_eq!(actors[1].x, 5);
    assert_eq!(actors[2].x, 8);
}
