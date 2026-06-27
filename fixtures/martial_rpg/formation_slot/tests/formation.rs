use martial_formation::{assign, Unit};

#[test]
fn highest_priority_gets_slot_zero() {
    let units = vec![
        Unit { id: 1, priority: 5 },
        Unit { id: 2, priority: 9 },
    ];
    // id 2 has higher priority -> slot 0; id 1 -> slot 1. Output sorted by id.
    assert_eq!(assign(&units, 2), vec![(1, 1), (2, 0)]);
}

#[test]
fn overflow_units_unassigned() {
    let units = vec![
        Unit { id: 1, priority: 3 },
        Unit { id: 2, priority: 7 },
        Unit { id: 3, priority: 1 },
    ];
    // only one slot: highest priority (id 2) gets slot 0, others -1.
    assert_eq!(assign(&units, 1), vec![(1, -1), (2, 0), (3, -1)]);
}

#[test]
fn ties_broken_by_id() {
    let units = vec![
        Unit { id: 7, priority: 4 },
        Unit { id: 3, priority: 4 },
    ];
    // equal priority -> lower id gets the lower slot.
    assert_eq!(assign(&units, 2), vec![(3, 0), (7, 1)]);
}
