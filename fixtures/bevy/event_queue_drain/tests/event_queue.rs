use event_queue_drain::events::{drain_collisions, Event};

#[test]
fn drains_only_collisions_and_preserves_other_events() {
    let mut events = vec![
        Event::AudioCue("jump"),
        Event::Collision(1, 2),
        Event::Score(50),
        Event::Collision(3, 4),
    ];

    let collisions = drain_collisions(&mut events);

    assert_eq!(collisions, vec![(1, 2), (3, 4)]);
    assert_eq!(events, vec![Event::AudioCue("jump"), Event::Score(50)]);
}
