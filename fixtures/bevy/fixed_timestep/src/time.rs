#[derive(Clone, Copy, Debug, PartialEq)]
pub struct FixedClock {
    pub step: f32,
    pub accumulator: f32,
    pub max_ticks: u32,
}

pub fn advance(clock: &mut FixedClock, delta: f32) -> u32 {
    clock.accumulator += delta;
    if clock.accumulator >= clock.step {
        clock.accumulator = 0.0;
        return 1;
    }
    0
}
