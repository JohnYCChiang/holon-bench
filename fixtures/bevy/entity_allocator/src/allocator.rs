/// A generational entity handle. The `generation` distinguishes a live entity
/// from a stale handle whose slot has since been recycled.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Entity {
    pub index: u32,
    pub generation: u32,
}

#[derive(Default, Debug)]
pub struct Allocator {
    generations: Vec<u32>,
    free_list: Vec<u32>,
}

impl Allocator {
    pub fn new() -> Self {
        Allocator { generations: Vec::new(), free_list: Vec::new() }
    }

    /// Allocate an entity, recycling a freed slot when one is available.
    pub fn allocate(&mut self) -> Entity {
        if let Some(index) = self.free_list.pop() {
            let generation = self.generations[index as usize];
            Entity { index, generation }
        } else {
            let index = self.generations.len() as u32;
            self.generations.push(0);
            Entity { index, generation: 0 }
        }
    }

    /// Free an entity, making its slot available for reuse.
    ///
    /// Freeing must invalidate every existing handle to this slot so that a
    /// later allocation cannot be mistaken for the freed entity (no
    /// use-after-free).
    pub fn free(&mut self, entity: Entity) {
        if !self.is_live(entity) {
            return;
        }
        self.free_list.push(entity.index);
    }

    /// Whether a handle still refers to a live entity.
    pub fn is_live(&self, entity: Entity) -> bool {
        self.generations.get(entity.index as usize) == Some(&entity.generation)
    }
}
