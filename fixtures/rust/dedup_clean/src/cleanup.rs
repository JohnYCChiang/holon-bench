/// Drop non-positive values, then collapse consecutive duplicates, in place.
pub fn clean(items: &mut Vec<i32>) {
    // BROKEN: dedup runs before the non-positive values are removed, so removing
    // them can leave new adjacent duplicates uncollapsed.
    items.dedup();
    items.retain(|&x| x > 0);
}
