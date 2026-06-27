#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Cooldown {
    pub remaining: f32,
    pub duration: f32,
}

impl Cooldown {
    pub fn new(duration: f32) -> Self {
        Cooldown { remaining: 0.0, duration }
    }
}

/// Advance a cooldown by `delta` seconds. The remaining time must never drop
/// below zero, otherwise a long pause would bank negative time and let an
/// ability fire early on the next frame.
pub fn tick(cd: &mut Cooldown, delta: f32) {
    cd.remaining -= delta;
}

pub fn is_ready(cd: &Cooldown) -> bool {
    cd.remaining <= 0.0
}

/// Try to use the ability. Returns true and re-arms the cooldown when ready,
/// otherwise returns false and leaves the cooldown untouched.
pub fn trigger(cd: &mut Cooldown) -> bool {
    if is_ready(cd) {
        cd.remaining = cd.duration;
        true
    } else {
        false
    }
}
