#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Shield {
    pub hp: i32,
    pub broken: bool,
}

impl Shield {
    pub fn new(hp: i32) -> Self {
        Shield { hp, broken: false }
    }
}

/// Apply `damage` to the shield and return the overflow that passes through to
/// the wearer. The shield absorbs up to its remaining hp; any excess passes
/// through. When the shield's hp reaches zero it becomes `broken`, and a broken
/// shield absorbs nothing (all later damage passes through). Non-positive damage
/// is a no-op.
pub fn absorb(s: &mut Shield, damage: i32) -> i32 {
    if damage <= 0 {
        return 0;
    }
    if s.broken {
        return damage;
    }
    let absorbed = damage.min(s.hp);
    s.hp -= absorbed;
    // BUG: forgets to flag the shield as broken once its hp is depleted.
    damage - absorbed
}
