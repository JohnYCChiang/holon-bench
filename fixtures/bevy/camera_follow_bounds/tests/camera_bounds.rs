use camera_follow_bounds::camera::{follow_position, Bounds, Vec2};

#[test]
fn follow_position_applies_offset_then_clamps_to_bounds() {
    let bounds = Bounds {
        min: Vec2 { x: 0.0, y: 0.0 },
        max: Vec2 { x: 100.0, y: 80.0 },
    };

    let position = follow_position(Vec2 { x: 95.0, y: -5.0 }, Vec2 { x: 20.0, y: 10.0 }, bounds);

    assert_eq!(position, Vec2 { x: 100.0, y: 5.0 });
}
