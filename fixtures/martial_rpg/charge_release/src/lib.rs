//! Authoritative charged-attack scaling. Damage grows linearly with how long an
//! attack was charged, between `min_charge` and `max_charge`, and the result is
//! deterministic and bounds-safe.

/// Resolve a charged attack. Charging below `min_charge` releases at `base` with
/// no bonus. Between `min_charge` and `max_charge` the bonus scales linearly from
/// 0 up to `max_bonus`; charging past `max_charge` adds nothing more. When
/// `max_charge <= min_charge` the full bonus applies once `charge_ticks` reaches
/// `min_charge`. The result saturates and never overflows.
pub fn release(
    base: u32,
    charge_ticks: u32,
    min_charge: u32,
    max_charge: u32,
    max_bonus: u32,
) -> u32 {
    // BUG: bonus scales with the raw charge ticks, ignoring the min/max clamps,
    // and can overflow.
    base + charge_ticks * max_bonus
}
