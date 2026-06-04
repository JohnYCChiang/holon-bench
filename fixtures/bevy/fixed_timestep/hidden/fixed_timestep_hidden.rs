use fixed_timestep::time::{advance, FixedClock};

#[test]
fn hidden_exact_step_produces_one_tick_without_remainder() {
    let mut clock = FixedClock {
        step: 0.25,
        accumulator: 0.0,
        max_ticks: 4,
    };

    assert_eq!(advance(&mut clock, 0.25), 1);
    assert!(clock.accumulator.abs() < 0.0001);
}

#[test]
fn hidden_zero_delta_preserves_fractional_accumulator() {
    let mut clock = FixedClock {
        step: 0.1,
        accumulator: 0.04,
        max_ticks: 4,
    };

    assert_eq!(advance(&mut clock, 0.0), 0);
    assert!((clock.accumulator - 0.04).abs() < 0.0001);
}
