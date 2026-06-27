use turn_order::initiative::{turn_order, Unit};

#[test]
fn ties_break_by_ascending_id() {
    // Input lists id 2 before id 1 among the speed-5 units; the result must
    // still order the tie by ascending id.
    let units = [
        Unit { id: 2, speed: 5 },
        Unit { id: 1, speed: 5 },
        Unit { id: 3, speed: 9 },
    ];
    assert_eq!(turn_order(&units), vec![3, 1, 2]);
}

#[test]
fn faster_units_act_first() {
    let units = [
        Unit { id: 10, speed: 1 },
        Unit { id: 11, speed: 8 },
        Unit { id: 12, speed: 4 },
    ];
    assert_eq!(turn_order(&units), vec![11, 12, 10]);
}
