use aabb_overlap::collision::{overlaps, Aabb};

fn aabb(min_x: f32, min_y: f32, max_x: f32, max_y: f32) -> Aabb {
    Aabb { min_x, min_y, max_x, max_y }
}

#[test]
fn separated_on_y_axis_does_not_overlap() {
    // Overlap on x, but b sits well above a -> no overlap.
    let a = aabb(0.0, 0.0, 10.0, 10.0);
    let b = aabb(5.0, 50.0, 15.0, 60.0);
    assert!(!overlaps(a, b));
}

#[test]
fn interpenetrating_boxes_overlap() {
    let a = aabb(0.0, 0.0, 10.0, 10.0);
    let b = aabb(5.0, 5.0, 15.0, 15.0);
    assert!(overlaps(a, b));
}
