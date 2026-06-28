/// Timing for an active-frame parry. After engage, the parry becomes active once
/// the `startup` delay has elapsed and stays active for `active` seconds.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ParryTiming {
    pub startup: f32,
    pub active: f32,
}

impl ParryTiming {
    pub fn new(startup: f32, active: f32) -> Self {
        ParryTiming { startup, active }
    }
}

/// Returns true if an attack arriving `t` seconds after engage is parried. The
/// active window is the half-open interval `[startup, startup + active)`.
pub fn parries(timing: &ParryTiming, t: f32) -> bool {
    // BUG: ignores the startup delay, so inputs during startup falsely parry and
    // the active window is measured from engage instead of from startup.
    t < timing.active
}
