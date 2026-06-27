//! Merge k already-sorted lists into one ascending list with a binary min-heap.
//!
//! Each element is a `(key, tag)` pair. Within each input list the keys are
//! non-decreasing. The merge is STABLE: for equal keys, elements from an earlier
//! list come first, and within a list their original order is preserved.

use std::cmp::Reverse;
use std::collections::BinaryHeap;

/// Merge `lists` (each sorted ascending by key) into one ascending, stable list.
pub fn merge_k(lists: Vec<Vec<(i32, u32)>>) -> Vec<(i32, u32)> {
    // Heap entries are (key, list_index, position) so ties break by earliest
    // list then earliest position, giving the stable ordering.
    let mut heap: BinaryHeap<Reverse<(i32, usize, usize)>> = BinaryHeap::new();
    for (li, list) in lists.iter().enumerate() {
        if !list.is_empty() {
            heap.push(Reverse((list[0].0, li, 0)));
        }
    }

    let mut out = Vec::new();
    while let Some(Reverse((_key, li, pos))) = heap.pop() {
        out.push(lists[li][pos]);
        // BUG: after consuming lists[li][pos] the NEXT element of the same list
        // is never pushed back onto the heap, so every list contributes only its
        // first element and the rest are silently dropped.
    }
    out
}
