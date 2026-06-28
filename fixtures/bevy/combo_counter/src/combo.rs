#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Combo {
    pub count: u32,
    pub timer: f32,
    pub window: f32,
}

impl Combo {
    pub fn new(window: f32) -> Self {
        Combo { count: 0, timer: 0.0, window }
    }
}

/// Register a hit. A hit landed while the window is still open grows the combo;
/// a hit after the window has lapsed starts a fresh combo at one. Every hit
/// resets the timer to the full window.
pub fn hit(c: &mut Combo) {
    c.count += 1;
    c.timer = c.window;
}

/// Advance time. When the window lapses with no hit the combo drops to zero and
/// the timer clamps at zero (never banking negative time).
pub fn tick(c: &mut Combo, delta: f32) {
    c.timer -= delta;
}

/// Damage multiplier tier derived from the current combo count.
pub fn multiplier(c: &Combo) -> u32 {
    (1 + c.count / 5).min(5)
}
