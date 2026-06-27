use spatial_hash::grid::{build_grid, cell_of};

#[test]
fn negative_coordinates_floor_into_lower_cell() {
    assert_eq!(cell_of(-0.5, -0.5, 1.0), (-1, -1));
    assert_eq!(cell_of(0.5, 0.5, 1.0), (0, 0));
    assert_eq!(cell_of(-1.0, 2.5, 1.0), (-1, 2));
}

#[test]
fn build_grid_buckets_points_across_origin() {
    let points = [(-0.5, 0.5), (0.5, 0.5), (-0.5, -0.5)];
    let grid = build_grid(&points, 1.0);
    assert_eq!(
        grid,
        vec![
            ((-1, -1), vec![2]),
            ((-1, 0), vec![0]),
            ((0, 0), vec![1]),
        ]
    );
}
