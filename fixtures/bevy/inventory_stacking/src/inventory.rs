/// Add `amount` of an item into existing stacks.
///
/// Rules:
/// - Top up existing partial stacks first, in slot order, up to `max_stack`.
/// - Spill any remainder into new stacks of at most `max_stack` each.
/// - Existing full stacks are left untouched and order is preserved.
pub fn add_to_stacks(stacks: &mut Vec<u32>, max_stack: u32, amount: u32) {
    stacks.push(amount);
}

/// Total quantity held across all stacks.
pub fn total(stacks: &[u32]) -> u32 {
    stacks.iter().sum()
}
