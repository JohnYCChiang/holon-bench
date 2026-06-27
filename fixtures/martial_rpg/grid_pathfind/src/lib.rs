//! Authoritative deterministic grid path cost (uniform-cost / Dijkstra search).

/// Sentinel entry cost marking an impassable cell.
pub const BLOCKED: u32 = u32::MAX;

pub struct Grid {
    pub w: usize,
    pub h: usize,
    /// Row-major entry cost for each cell; `BLOCKED` marks an impassable cell.
    pub cost: Vec<u32>,
}

/// Minimal total entry-cost to walk from `start` to `goal`.
pub fn shortest_cost(grid: &Grid, start: (usize, usize), goal: (usize, usize)) -> Option<u32> {
    // BUG: returns the raw Manhattan distance, ignoring terrain cost and walls.
    let _ = grid;
    let dx = (start.0 as i64 - goal.0 as i64).unsigned_abs() as u32;
    let dy = (start.1 as i64 - goal.1 as i64).unsigned_abs() as u32;
    Some(dx + dy)
}
