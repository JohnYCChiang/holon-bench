use martial_replay::{replay_checksum, Event};

#[test]
fn replay_is_independent_of_delivery_order() {
    let delivered_a = vec![
        Event { entity_id: 3, delta: 10 },
        Event { entity_id: 1, delta: -2 },
        Event { entity_id: 2, delta: 5 },
    ];
    let delivered_b = vec![
        Event { entity_id: 1, delta: -2 },
        Event { entity_id: 2, delta: 5 },
        Event { entity_id: 3, delta: 10 },
    ];
    assert_eq!(replay_checksum(&delivered_a), replay_checksum(&delivered_b));
}

#[test]
fn distinct_replays_have_distinct_checksums() {
    let a = vec![Event { entity_id: 1, delta: 1 }];
    let b = vec![Event { entity_id: 1, delta: 2 }];
    assert_ne!(replay_checksum(&a), replay_checksum(&b));
}
