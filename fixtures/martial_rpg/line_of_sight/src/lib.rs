//! Authoritative grid line-of-sight. A target is visible from a source when no
//! blocked cell lies strictly between them along the traced line. The trace is
//! deterministic and symmetric (the same result regardless of which endpoint is
//! the source).

pub struct Grid {
    pub width: i32,
    pub height: i32,
    /// Coordinates of blocked (sight-blocking) cells.
    pub blocked: Vec<(i32, i32)>,
}

impl Grid {
    fn in_bounds(&self, p: (i32, i32)) -> bool {
        p.0 >= 0 && p.0 < self.width && p.1 >= 0 && p.1 < self.height
    }

    fn is_blocked(&self, p: (i32, i32)) -> bool {
        self.blocked.iter().any(|&b| b == p)
    }
}

/// Returns true if `to` is visible from `from`.
///
/// Both endpoints must be in bounds. The endpoints themselves never block sight;
/// only intermediate cells do. The same cell is trivially visible. The result is
/// symmetric: `has_los(g, a, b) == has_los(g, b, a)`.
pub fn has_los(grid: &Grid, from: (i32, i32), to: (i32, i32)) -> bool {
    // BUG: ignores blockers entirely and always reports clear sight.
    let _ = (grid, from, to);
    true
}
