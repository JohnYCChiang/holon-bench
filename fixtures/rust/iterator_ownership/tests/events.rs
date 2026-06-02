use iterator_ownership::events::{summarize, Event};

#[test]
fn summarize_does_not_consume_caller_buffer() {
    let events = vec![
        Event { player: "a".to_string(), points: 2 },
        Event { player: "b".to_string(), points: 3 },
    ];
    assert_eq!(summarize(&events), (2, 5));
    assert_eq!(events[0].player, "a");
}
