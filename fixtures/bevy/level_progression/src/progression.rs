/// Compute the current level given total accumulated XP.
///
/// `thresholds` lists the cumulative XP required to *reach* each successive
/// level, in ascending order. The player starts at level 1; reaching a
/// threshold exactly is enough to gain that level.
///
/// Example: thresholds [100, 250, 500]
///   xp 0   -> level 1
///   xp 100 -> level 2 (threshold reached exactly)
///   xp 499 -> level 3
///   xp 500 -> level 4
pub fn level_for_xp(total_xp: u32, thresholds: &[u32]) -> u32 {
    let mut level = 1;
    for &t in thresholds {
        if total_xp > t {
            level += 1;
        }
    }
    level
}
