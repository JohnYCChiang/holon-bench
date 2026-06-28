#[derive(Clone, Debug)]
pub struct FogMap {
    pub width: i32,
    pub height: i32,
    explored: Vec<bool>,
}

impl FogMap {
    pub fn new(width: i32, height: i32) -> Self {
        FogMap { width, height, explored: vec![false; (width * height) as usize] }
    }

    fn in_bounds(&self, x: i32, y: i32) -> bool {
        x >= 0 && x < self.width && y >= 0 && y < self.height
    }

    fn idx(&self, x: i32, y: i32) -> usize {
        (y * self.width + x) as usize
    }

    pub fn is_explored(&self, x: i32, y: i32) -> bool {
        self.in_bounds(x, y) && self.explored[self.idx(x, y)]
    }

    pub fn explored_count(&self) -> usize {
        self.explored.iter().filter(|&&e| e).count()
    }

    /// Reveal every in-bounds tile within Chebyshev `radius` of (cx, cy).
    /// Revealing is cumulative: previously explored tiles stay explored.
    pub fn reveal(&mut self, cx: i32, cy: i32, radius: i32) {
        for y in 0..self.height {
            for x in 0..self.width {
                let d = (x - cx).abs().max((y - cy).abs());
                let visible = d < radius;
                let i = self.idx(x, y);
                self.explored[i] = visible;
            }
        }
    }
}
