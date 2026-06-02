#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Vec2 {
    pub x: f32,
    pub y: f32,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Bounds {
    pub min: Vec2,
    pub max: Vec2,
}

pub fn follow_position(target: Vec2, offset: Vec2, _bounds: Bounds) -> Vec2 {
    Vec2 { x: target.x + offset.x, y: target.y + offset.y }
}
