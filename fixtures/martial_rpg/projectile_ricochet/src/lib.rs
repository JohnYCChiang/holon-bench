//! Authoritative projectile ricochet chain. A bouncing projectile hops from the
//! origin to the nearest in-range target, then from each hit target to the
//! nearest not-yet-hit in-range target, up to a bounce cap. Each target is hit
//! at most once and the chain is fully deterministic.

/// Compute the ordered chain of target indices a ricocheting projectile hits.
///
/// Starting at `origin`, repeatedly jump to the nearest unhit target whose
/// squared distance from the current position is `<= max_range^2`, breaking ties
/// by lowest index. Stops when no target is in range or after `max_bounces`
/// hits. A negative `max_range` reaches nothing. No target appears twice.
pub fn ricochet_chain(
    origin: (i32, i32),
    targets: &[(i32, i32)],
    max_range: i32,
    max_bounces: u32,
) -> Vec<usize> {
    // BUG: ignores range and the bounce cap, never marks targets as hit, and
    // walks the slice in raw order so the same target can be "hit" repeatedly.
    let mut out = Vec::new();
    let _ = (origin, max_range);
    for _ in 0..max_bounces {
        for i in 0..targets.len() {
            out.push(i);
        }
    }
    out
}
