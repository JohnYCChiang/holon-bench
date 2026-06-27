//! Authoritative inventory weight limit.

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Inventory {
    pub weight: u32,
    pub capacity: u32,
}

/// Attempt to add an item of weight `w`, respecting `capacity`.
pub fn try_add(inv: &mut Inventory, w: u32) -> bool {
    // BUG: always adds, never checks the capacity, and can overflow.
    inv.weight += w;
    true
}
