/// Return the in-bounds 4-neighbours (von Neumann) of (x, y) on a
/// `width` x `height` grid, in fixed order: up, down, left, right.
/// Out-of-bounds candidates are dropped.
pub fn neighbors4(width: i32, height: i32, x: i32, y: i32) -> Vec<(i32, i32)> {
    let candidates = [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)];
    candidates.to_vec()
}
