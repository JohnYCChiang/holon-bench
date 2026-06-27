use spawn_scheduler::spawner::{step, Spawner};

#[test]
fn does_not_exceed_wave_budget() {
    let mut s = Spawner { interval: 1.0, accumulator: 0.0, remaining: 2 };
    let spawned = step(&mut s, 5.0);
    assert_eq!(spawned, 2);
    assert_eq!(s.remaining, 0);
    // Two intervals consumed; the rest of the banked time is preserved.
    assert!((s.accumulator - 3.0).abs() < 1e-6);
}

#[test]
fn spawns_at_each_interval() {
    let mut s = Spawner { interval: 0.5, accumulator: 0.0, remaining: 10 };
    let spawned = step(&mut s, 1.6);
    assert_eq!(spawned, 3);
    assert_eq!(s.remaining, 7);
    assert!((s.accumulator - 0.1).abs() < 1e-6);
}
