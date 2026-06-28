#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Vec2 {
    pub x: f32,
    pub y: f32,
}

impl Vec2 {
    pub fn new(x: f32, y: f32) -> Self {
        Vec2 { x, y }
    }
}

fn dist(a: Vec2, b: Vec2) -> f32 {
    let dx = a.x - b.x;
    let dy = a.y - b.y;
    (dx * dx + dy * dy).sqrt()
}

/// Decide where an enemy moves this frame. If the enemy has strayed strictly
/// farther than `leash` from its `home` anchor it disengages and returns to
/// `home`; otherwise it keeps chasing `target`. The leash boundary is inclusive
/// -- an enemy exactly `leash` away still chases.
pub fn decide(home: Vec2, enemy: Vec2, target: Vec2, leash: f32) -> Vec2 {
    // BUG: measures the leash from the target instead of from home.
    if dist(enemy, target) > leash {
        home
    } else {
        target
    }
}
