#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Pool {
    pub current: i32,
    pub max: i32,
    pub accum: f32,
}

impl Pool {
    pub fn new(current: i32, max: i32) -> Self {
        Pool { current, max, accum: 0.0 }
    }
}

/// Regenerate the pool over `delta` seconds at `rate` points per second. Whole
/// points are added to `current`, and fractional progress carries over in
/// `accum`. `current` is capped at `max`; once the pool is full the leftover
/// accumulator is discarded so a later drain does not instantly refill.
pub fn regen(p: &mut Pool, delta: f32, rate: f32) {
    // BUG: never caps at max and keeps banking the accumulator past full.
    p.accum += delta * rate;
    let whole = p.accum.floor() as i32;
    p.accum -= whole as f32;
    p.current += whole;
}
