use fixed_timestep::time::{advance, FixedClock};

#[test]
fn mutation_capped_backlog_is_drained_by_later_frames() {
    let mut clock = FixedClock {
        step: 0.1,
        accumulator: 0.0,
        max_ticks: 4,
    };

    assert_eq!(advance(&mut clock, 1.0), 4);
    assert!((clock.accumulator - 0.6).abs() < 0.0001);

    assert_eq!(advance(&mut clock, 0.0), 4);
    assert!((clock.accumulator - 0.2).abs() < 0.0001);

    assert_eq!(advance(&mut clock, 0.0), 2);
    assert!(clock.accumulator.abs() < 0.0001);
}
