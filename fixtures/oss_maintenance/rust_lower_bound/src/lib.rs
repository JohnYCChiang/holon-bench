//! Leftmost binary search over an ascending-sorted slice.

/// Return the index of the first element of `a` that is `>= target`
/// (equivalently, the number of elements strictly less than `target`). `a` must
/// be sorted ascending. For a target present multiple times this is the index
/// of the FIRST occurrence; for an absent target it is the leftmost insertion
/// point that keeps `a` sorted.
pub fn lower_bound(a: &[i64], target: i64) -> usize {
    let mut lo = 0usize;
    let mut hi = a.len();
    while lo < hi {
        let mid = lo + (hi - lo) / 2;
        if a[mid] <= target {
            // BUG: `<=` skips past equal elements, yielding an UPPER bound;
            // the leftmost index requires the strict comparison `<`.
            lo = mid + 1;
        } else {
            hi = mid;
        }
    }
    lo
}
