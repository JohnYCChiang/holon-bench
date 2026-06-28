#[derive(Clone, Copy, Debug, PartialEq)]
pub enum BuffKind {
    Refresh,
    Stack,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct BuffDef {
    pub id: u32,
    pub kind: BuffKind,
    pub max_stacks: u32,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ActiveBuff {
    pub id: u32,
    pub stacks: u32,
    pub duration: f32,
}

/// Apply a buff to an active list.
///
/// - Each id may have at most one active entry.
/// - `Refresh` buffs keep a single stack and extend to the longer duration.
/// - `Stack` buffs increment stacks up to `max_stacks` and reset duration.
pub fn apply(active: &mut Vec<ActiveBuff>, def: &BuffDef, duration: f32) {
    active.push(ActiveBuff { id: def.id, stacks: 1, duration });
}
