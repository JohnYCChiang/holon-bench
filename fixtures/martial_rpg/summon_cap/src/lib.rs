//! Authoritative summon manager. The server owns the set of active summoned
//! entities and must enforce the per-summoner cap and reject duplicate ids,
//! regardless of what the client asks for.

pub struct Summoner {
    pub max_active: usize,
    active: Vec<u32>,
}

impl Summoner {
    pub fn new(max_active: usize) -> Self {
        Summoner {
            max_active,
            active: Vec::new(),
        }
    }

    /// Attempt to summon entity `id`. Succeeds (returns true) only when the
    /// summoner is below its cap and `id` is not already active; otherwise the
    /// active set is left unchanged and it returns false.
    pub fn summon(&mut self, id: u32) -> bool {
        self.active.push(id); // BUG: ignores the cap and duplicate ids
        true
    }

    /// Dismiss entity `id`, freeing a slot. Returns true if it was active.
    pub fn dismiss(&mut self, id: u32) -> bool {
        if let Some(pos) = self.active.iter().position(|&x| x == id) {
            self.active.remove(pos);
            true
        } else {
            false
        }
    }

    pub fn count(&self) -> usize {
        self.active.len()
    }

    /// The active entity ids in ascending order (order-independent view).
    pub fn active(&self) -> Vec<u32> {
        self.active.clone() // BUG: not sorted; leaks insertion order
    }
}
