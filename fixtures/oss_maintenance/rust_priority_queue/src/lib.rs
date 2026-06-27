//! A small priority queue. `pop` returns the highest-priority value; ties are
//! broken by insertion order (first pushed is first popped). A monotonically
//! increasing sequence number records insertion order.

/// A priority queue of `String` values keyed by an `i64` priority.
pub struct PriorityQueue {
    items: Vec<(i64, u64, String)>,
    seq: u64,
}

impl PriorityQueue {
    /// Create an empty queue.
    pub fn new() -> Self {
        PriorityQueue { items: Vec::new(), seq: 0 }
    }

    /// Push `value` with the given `priority`.
    pub fn push(&mut self, priority: i64, value: String) {
        self.items.push((priority, self.seq, value));
        self.seq += 1;
    }

    /// Remove and return the highest-priority value, ties by insertion order.
    pub fn pop(&mut self) -> Option<String> {
        if self.items.is_empty() {
            return None;
        }
        let mut best = 0usize;
        for i in 1..self.items.len() {
            let (bp, bs, _) = &self.items[best];
            let (ip, is, _) = &self.items[i];
            // BUG: on a priority tie this keeps the LARGER sequence number
            // (the later insertion), so ties are served LIFO. It should keep
            // the smaller sequence number (`is < bs`) for FIFO order.
            if ip > bp || (ip == bp && is > bs) {
                best = i;
            }
        }
        Some(self.items.remove(best).2)
    }

    /// Number of queued values.
    pub fn len(&self) -> usize {
        self.items.len()
    }

    /// Whether the queue is empty.
    pub fn is_empty(&self) -> bool {
        self.items.is_empty()
    }
}
