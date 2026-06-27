#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Aabb {
    pub min_x: f32,
    pub min_y: f32,
    pub max_x: f32,
    pub max_y: f32,
}

/// Axis-aligned bounding box overlap test.
///
/// Two boxes overlap when they intersect on *both* axes. Boxes that merely
/// touch along an edge (shared boundary) are treated as overlapping.
pub fn overlaps(a: Aabb, b: Aabb) -> bool {
    a.min_x <= b.max_x && a.max_x >= b.min_x
}
