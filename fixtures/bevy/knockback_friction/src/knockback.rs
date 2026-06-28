#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Velocity {
    pub vx: f32,
    pub vy: f32,
}

/// Apply friction deceleration to a knockback velocity. Speed decreases by
/// `friction * delta` toward zero and must never reverse direction
/// (overshoot past zero). When the drop exceeds the current speed the velocity
/// snaps to exactly zero.
pub fn apply_friction(v: &mut Velocity, friction: f32, delta: f32) {
    let drop = friction * delta;
    v.vx -= drop * v.vx.signum();
    v.vy -= drop * v.vy.signum();
}
