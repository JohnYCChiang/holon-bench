/// Compute the x-offsets of `count` units arranged in a row, spaced `spacing`
/// apart and centered on zero. For count=3, spacing=2.0 -> [-2.0, 0.0, 2.0]; for
/// count=2, spacing=2.0 -> [-1.0, 1.0]. count=0 yields an empty row.
pub fn slot_offsets(count: u32, spacing: f32) -> Vec<f32> {
    // BUG: lays the row out starting at zero instead of centering it.
    (0..count).map(|i| i as f32 * spacing).collect()
}
