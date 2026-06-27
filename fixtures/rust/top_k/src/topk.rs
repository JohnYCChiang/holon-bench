use std::collections::BinaryHeap;

/// Return the `k` largest values in descending order.
pub fn top_k(values: &[i64], k: usize) -> Vec<i64> {
    let mut heap: BinaryHeap<i64> = values.iter().copied().collect();
    let mut out = Vec::new();
    for _ in 0..k {
        match heap.pop() {
            Some(v) => out.push(v),
            None => break,
        }
    }
    // BROKEN: re-sorts ascending, destroying the required descending order.
    out.sort();
    out
}
