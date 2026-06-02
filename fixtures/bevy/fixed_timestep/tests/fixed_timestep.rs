use fixed_timestep::time::{advance, FixedClock};

#[test]
fn accumulates_multiple_ticks_and_keeps_fractional_remainder() {
    let mut clock = FixedClock { step: 0.1, accumulator: 0.04, max_ticks: 4 };

    let ticks = advance(&mut clock, 0.31);

    assert_eq!(ticks, 3);
    assert!((clock.accumulator - 0.05).abs() < 0.0001);
}

#[test]
fn caps_runaway_catch_up_ticks() {
    let mut clock = FixedClock { step: 0.1, accumulator: 0.0, max_ticks: 4 };

    let ticks = advance(&mut clock, 1.0);

    assert_eq!(ticks, 4);
    assert!((clock.accumulator - 0.6).abs() < 0.0001);
}
