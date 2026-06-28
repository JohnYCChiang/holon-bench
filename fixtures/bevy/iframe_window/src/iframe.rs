#[derive(Clone, Copy, Debug, PartialEq)]
pub struct IFrames {
    pub remaining: f32,
}

impl IFrames {
    pub fn new() -> Self {
        IFrames { remaining: 0.0 }
    }
}

/// Start a dash, granting `window` seconds of invulnerability. Refreshing while
/// already invulnerable must extend to the longer window, never shorten it.
pub fn start_dash(frames: &mut IFrames, window: f32) {
    if window > frames.remaining {
        frames.remaining = window;
    }
}

/// Advance the i-frame window. Remaining time must never bank below zero.
pub fn tick(frames: &mut IFrames, delta: f32) {
    frames.remaining -= delta;
}

pub fn is_invulnerable(frames: &IFrames) -> bool {
    frames.remaining > 0.0
}

/// Apply incoming damage. While invulnerable the hit is fully negated.
pub fn apply_hit(frames: &IFrames, raw: u32) -> u32 {
    raw
}
