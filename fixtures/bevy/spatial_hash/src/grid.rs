use std::collections::BTreeMap;

/// Map a world position to its grid cell coordinate.
///
/// Cells tile the whole plane, including negative space, so this must use
/// floored division rather than truncation toward zero. A point at x = -0.5
/// with cell size 1.0 lives in cell -1, not cell 0.
pub fn cell_of(x: f32, y: f32, cell_size: f32) -> (i32, i32) {
    ((x / cell_size) as i32, (y / cell_size) as i32)
}

/// Bucket points into grid cells for broad-phase neighbor lookups.
///
/// Returns cells in deterministic ascending coordinate order, each holding the
/// indices of the points it contains in their original order.
pub fn build_grid(points: &[(f32, f32)], cell_size: f32) -> Vec<((i32, i32), Vec<usize>)> {
    let mut cells: BTreeMap<(i32, i32), Vec<usize>> = BTreeMap::new();
    for (i, &(x, y)) in points.iter().enumerate() {
        cells.entry(cell_of(x, y, cell_size)).or_default().push(i);
    }
    cells.into_iter().collect()
}
