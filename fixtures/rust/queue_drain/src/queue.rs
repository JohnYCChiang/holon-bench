use std::collections::VecDeque;

#[derive(Default)]
pub struct Queue {
    items: VecDeque<i32>,
}

impl Queue {
    pub fn push(&mut self, item: i32) {
        self.items.push_back(item);
    }

    pub fn drain_ready(&mut self, limit: usize) -> Vec<i32> {
        let mut out = Vec::new();
        while let Some(item) = self.items.pop_back() {
            out.push(item);
            if out.len() == limit {
                self.items.clear();
                break;
            }
        }
        out
    }
}
